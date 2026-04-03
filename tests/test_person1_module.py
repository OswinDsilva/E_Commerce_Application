from datetime import date
import unittest

from backend.errors import ApiError
from backend.services.payment_service import pay_for_order
from backend.utils.auth import require_same_user
from backend.utils.passwords import hash_password, verify_password
from backend.utils.sessions import (
    clear_user_sessions,
    create_session,
    destroy_session,
    get_session_user_id,
)


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.current_step = None
        self.rowcount = 0

    def execute(self, query, params=None):
        if self.connection.step_index >= len(self.connection.steps):
            raise AssertionError(f"Unexpected query: {query!r} {params!r}")

        self.current_step = self.connection.steps[self.connection.step_index]
        self.connection.step_index += 1
        self.rowcount = self.current_step.get("rowcount", 0)

    def fetchone(self):
        if self.current_step is None:
            raise AssertionError("fetchone() called before execute()")
        return self.current_step.get("fetchone")

    def fetchall(self):
        if self.current_step is None:
            raise AssertionError("fetchall() called before execute()")
        return self.current_step.get("fetchall", [])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, steps):
        self.steps = steps
        self.step_index = 0

    def cursor(self):
        return FakeCursor(self)


class PasswordAndSessionTests(unittest.TestCase):
    def tearDown(self):
        clear_user_sessions(10)

    def test_password_hash_and_verify(self):
        stored_hash = hash_password("secret123")
        self.assertNotEqual(stored_hash, "secret123")
        self.assertTrue(verify_password("secret123", stored_hash))
        self.assertFalse(verify_password("wrong", stored_hash))

    def test_session_lifecycle(self):
        token = create_session({"u_id": 10})
        self.assertEqual(get_session_user_id(token), 10)
        destroy_session(token)
        self.assertIsNone(get_session_user_id(token))


class OwnershipTests(unittest.TestCase):
    def test_require_same_user_rejects_other_user(self):
        with self.assertRaises(ApiError) as context:
            require_same_user(2, {"u_id": 1, "role": "USER"})

        self.assertEqual(context.exception.code, "UNAUTHORIZED")


class PaymentServiceTests(unittest.TestCase):
    def test_pay_for_order_rejects_other_users_account(self):
        connection = FakeConnection(
            [
                {
                    "fetchone": {
                        "o_id": 7,
                        "order_date": date(2026, 4, 3),
                        "status": "CREATED",
                        "total_amount": 1299.5,
                        "u_id": 1,
                        "acc_no": None,
                    }
                },
                {
                    "fetchone": {
                        "acc_no": 999,
                        "bank_name": "Test Bank",
                        "expiry_date": date(2027, 1, 1),
                        "u_id": 2,
                    }
                },
            ]
        )

        with self.assertRaises(ApiError) as context:
            pay_for_order(connection, 7, 999, {"u_id": 1, "role": "USER"})

        self.assertEqual(context.exception.code, "INVALID_ACCOUNT")

    def test_pay_for_order_marks_order_paid(self):
        connection = FakeConnection(
            [
                {
                    "fetchone": {
                        "o_id": 9,
                        "order_date": date(2026, 4, 3),
                        "status": "CREATED",
                        "total_amount": 2500.0,
                        "u_id": 1,
                        "acc_no": None,
                    }
                },
                {
                    "fetchone": {
                        "acc_no": 1234,
                        "bank_name": "Valid Bank",
                        "expiry_date": date(2027, 5, 1),
                        "u_id": 1,
                    }
                },
                {"rowcount": 1},
                {
                    "fetchone": {
                        "o_id": 9,
                        "order_date": date(2026, 4, 3),
                        "status": "PAID",
                        "total_amount": 2500.0,
                        "u_id": 1,
                        "acc_no": 1234,
                    }
                },
                {"fetchone": None},
            ]
        )

        result = pay_for_order(connection, 9, 1234, {"u_id": 1, "role": "USER"})

        self.assertEqual(result["order"]["status"], "PAID")
        self.assertEqual(result["order"]["acc_no"], 1234)
        self.assertIsNone(result["invoice"])


if __name__ == "__main__":
    unittest.main()
