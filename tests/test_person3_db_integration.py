from datetime import date
import json
import unittest

import pymysql

from backend.config import TEST_DATABASE_URL


@unittest.skipIf(TEST_DATABASE_URL is None, "TEST_DATABASE_URL is not configured")
class Person3DatabaseIntegrationTests(unittest.TestCase):
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
        self._reset_data()
        self._seed_data()
        self.connection.commit()

    def tearDown(self):
        self.connection.rollback()

    def _reset_data(self):
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

    def _seed_data(self):
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
            cursor.execute("INSERT INTO categories (id, category) VALUES (1, 'Clothing')")
            cursor.execute(
                """
                INSERT INTO Products (p_id, product_name, brand, price, category_id, description)
                VALUES
                    (501, 'Shirt', 'Atelier', 20.00, 1, 'Cotton shirt'),
                    (502, 'Jacket', 'Atelier', 80.00, 1, 'Winter jacket')
                """
            )
            cursor.execute(
                """
                INSERT INTO Inventory (p_id, quantity, last_updated)
                VALUES
                    (501, 5, NOW()),
                    (502, 2, NOW())
                """
            )

    def test_sp_create_order_with_items_creates_order_and_deducts_stock(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "CALL sp_create_order_with_items(%s, %s, %s, %s)",
                (
                    101,
                    "123 Demo Street",
                    "123 Demo Street",
                    json.dumps([
                        {"p_id": 501, "quantity": 2},
                        {"p_id": 502, "quantity": 1},
                    ]),
                ),
            )
            order = cursor.fetchone()

            cursor.execute("SELECT quantity FROM Inventory WHERE p_id = %s", (501,))
            shirt_stock = cursor.fetchone()["quantity"]
            cursor.execute("SELECT quantity FROM Inventory WHERE p_id = %s", (502,))
            jacket_stock = cursor.fetchone()["quantity"]

        self.assertEqual(order["status"], "CREATED")
        self.assertEqual(float(order["total_amount"]), 120.0)
        self.assertEqual(shirt_stock, 3)
        self.assertEqual(jacket_stock, 1)

    def test_sp_add_order_items_rejects_when_insufficient_stock(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "CALL sp_create_order_with_items(%s, %s, %s, %s)",
                (
                    101,
                    "123 Demo Street",
                    "123 Demo Street",
                    json.dumps([{"p_id": 501, "quantity": 1}]),
                ),
            )
            order = cursor.fetchone()

            with self.assertRaises(pymysql.MySQLError) as context:
                cursor.execute(
                    "CALL sp_add_order_items(%s, %s, %s)",
                    (order["o_id"], 101, json.dumps([{"p_id": 502, "quantity": 5}])),
                )

        self.assertIn("OUT_OF_STOCK", str(context.exception))

    def test_sp_generate_invoice_after_payment(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "CALL sp_create_order_with_items(%s, %s, %s, %s)",
                (
                    101,
                    "123 Demo Street",
                    "123 Demo Street",
                    json.dumps([{"p_id": 501, "quantity": 1}]),
                ),
            )
            order = cursor.fetchone()

            cursor.execute("CALL sp_pay_order(%s, %s, %s)", (order["o_id"], 101, 2001))
            cursor.fetchone()

            cursor.execute("CALL sp_generate_invoice(%s, %s)", (order["o_id"], 101))
            invoice = cursor.fetchone()

        self.assertEqual(invoice["o_id"], order["o_id"])
        self.assertEqual(invoice["shipping_address"], "123 Demo Street")


if __name__ == "__main__":
    unittest.main()
