from datetime import date
import unittest

import pymysql

from backend.config import TEST_DATABASE_URL


@unittest.skipIf(TEST_DATABASE_URL is None, "TEST_DATABASE_URL is not configured")
class Person1DatabaseIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.connection = pymysql.connect(
                host=TEST_DATABASE_URL["host"],
                user=TEST_DATABASE_URL["user"],
                password=TEST_DATABASE_URL["password"],
                database=TEST_DATABASE_URL["database"],
                port=TEST_DATABASE_URL.get("port", 3306),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
        except RuntimeError as exc:
            raise unittest.SkipTest(str(exc)) from exc

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        self._reset_person1_data()
        self._seed_person1_data()
        self.connection.commit()

    def tearDown(self):
        self.connection.rollback()

    def _reset_person1_data(self):
        with self.connection.cursor() as cursor:
            for table_name in (
                "ordered_items",
                "Invoice",
                "Orders",
                "Inventory",
                "Products",
                "Bank_acc",
                "Users",
                "categories",
                "roles",
            ):
                cursor.execute(f"DELETE FROM {table_name}")

    def _seed_person1_data(self):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO roles (id, role) VALUES (1, 'ADMIN'), (2, 'USER')")
            cursor.execute(
                """
                INSERT INTO Users (u_id, username, password_hash, email, phone, role_id)
                VALUES
                    (101, 'owner', 'hash', 'owner@example.com', '1111111111', 2),
                    (102, 'other', 'hash', 'other@example.com', '2222222222', 2)
                """
            )
            cursor.execute(
                """
                INSERT INTO Bank_acc (acc_no, bank_name, expiry_date, u_id)
                VALUES
                    (2001, 'Owner Bank', %s, 101),
                    (2002, 'Other Bank', %s, 102)
                """,
                (date(2027, 1, 1), date(2027, 1, 1)),
            )
            cursor.execute(
                """
                INSERT INTO Orders (o_id, order_date, status, total_amount, u_id, acc_no)
                VALUES
                    (3001, %s, 'CREATED', 99.99, 101, NULL),
                    (3002, %s, 'CREATED', 19.99, 101, NULL)
                """,
                (date(2026, 4, 1), date(2026, 4, 2)),
            )

    def test_sp_register_user_rejects_duplicate_username(self):
        with self.connection.cursor() as cursor:
            with self.assertRaises(pymysql.MySQLError) as context:
                cursor.execute(
                    "CALL sp_register_user(%s, %s, %s, %s, %s, %s)",
                    (150, "owner", "hashed", "new@example.com", "3333333333", 2),
                )

        self.assertIn("Username already exists", str(context.exception))

    def test_sp_pay_order_marks_order_paid(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "CALL sp_pay_order(%s, %s, %s)",
                (3001, 101, 2001),
            )
            row = cursor.fetchone()

        self.assertEqual(row["status"], "PAID")
        self.assertEqual(row["acc_no"], 2001)

    def test_orders_trigger_blocks_foreign_bank_account(self):
        with self.connection.cursor() as cursor:
            with self.assertRaises(pymysql.MySQLError) as context:
                cursor.execute(
                    """
                    UPDATE Orders
                    SET status = 'PAID', acc_no = %s
                    WHERE o_id = %s
                    """,
                    (2002, 3002),
                )

        self.assertIn("INVALID_ACCOUNT", str(context.exception))


if __name__ == "__main__":
    unittest.main()
