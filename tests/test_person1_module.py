from datetime import date
from decimal import Decimal
from datetime import datetime
import unittest

from pymysql.err import OperationalError

from backend.errors import ApiError
from backend.schemas.auth import RegisterRequest
from backend.schemas.bank_accounts import BankAccountOut, CreateBankAccountRequest
from backend.schemas.payments import PayOrderRequest
from backend.schemas.users import AuthenticatedUser
from backend.services.auth_service import register_user
from backend.services.bank_account_service import add_bank_account, delete_bank_account
from backend.services.payment_service import pay_for_order
from backend.services.user_service import delete_user
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
        error = self.current_step.get("execute_error")
        if error is not None:
            raise error
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

    def nextset(self):
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
            require_same_user(
                2,
                AuthenticatedUser(
                    u_id=1,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "UNAUTHORIZED")


class AuthServiceProcedureTests(unittest.TestCase):
    def test_register_user_rejects_duplicate_username_from_procedure(self):
        connection = FakeConnection(
            [
                {"fetchone": {"next_id": 11}},
                {"fetchone": {"id": 2}},
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|BAD_REQUEST|400|Username already exists",
                    )
                },
            ]
        )

        with self.assertRaises(ApiError) as context:
            register_user(
                connection,
                RegisterRequest(
                    username="existing-user",
                    password="secret123",
                    email="new@example.com",
                    phone="9999999999",
                ),
            )

        self.assertEqual(context.exception.code, "BAD_REQUEST")
        self.assertEqual(context.exception.message, "Username already exists")

    def test_register_user_rejects_duplicate_email_from_procedure(self):
        connection = FakeConnection(
            [
                {"fetchone": {"next_id": 11}},
                {"fetchone": {"id": 2}},
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|BAD_REQUEST|400|Email already exists",
                    )
                },
            ]
        )

        with self.assertRaises(ApiError) as context:
            register_user(
                connection,
                RegisterRequest(
                    username="new-user",
                    password="secret123",
                    email="existing@example.com",
                    phone="9999999999",
                ),
            )

        self.assertEqual(context.exception.code, "BAD_REQUEST")
        self.assertEqual(context.exception.message, "Email already exists")


class BankAccountProcedureTests(unittest.TestCase):
    def test_add_bank_account_rejects_duplicate_account(self):
        connection = FakeConnection(
            [
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|BAD_REQUEST|400|Bank account already exists",
                    )
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            add_bank_account(
                connection,
                CreateBankAccountRequest(
                    acc_no=1234,
                    bank_name="Demo Bank",
                    expiry_date=date(2027, 5, 1),
                ),
                AuthenticatedUser(
                    u_id=1,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "BAD_REQUEST")
        self.assertEqual(context.exception.message, "Bank account already exists")

    def test_delete_bank_account_returns_not_found_when_missing_or_foreign(self):
        connection = FakeConnection(
            [
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|NOT_FOUND|404|Bank account not found",
                    )
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            delete_bank_account(
                connection,
                8888,
                AuthenticatedUser(
                    u_id=1,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "NOT_FOUND")


class UserProcedureTests(unittest.TestCase):
    def test_delete_user_returns_not_found_when_missing(self):
        connection = FakeConnection(
            [
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|NOT_FOUND|404|User not found",
                    )
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            delete_user(
                connection,
                99,
                AuthenticatedUser(
                    u_id=99,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "NOT_FOUND")


class PaymentServiceTests(unittest.TestCase):
    def test_pay_for_order_rejects_other_users_account(self):
        connection = FakeConnection(
            [
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|INVALID_ACCOUNT|400|Selected bank account is invalid",
                    )
                },
            ]
        )

        with self.assertRaises(ApiError) as context:
            pay_for_order(
                connection,
                7,
                PayOrderRequest(acc_no=999),
                AuthenticatedUser(
                    u_id=1,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "INVALID_ACCOUNT")

    def test_pay_for_order_marks_order_paid(self):
        connection = FakeConnection(
            [
                {
                    "fetchone": {
                        "o_id": 9,
                        "order_date": date(2026, 4, 3),
                        "status": "PAID",
                        "total_amount": Decimal("2500.0"),
                        "u_id": 1,
                        "acc_no": 1234,
                    }
                },
                {"fetchone": None},
            ]
        )

        result = pay_for_order(
            connection,
            9,
            PayOrderRequest(acc_no=1234),
            AuthenticatedUser(
                u_id=1,
                username="owner",
                email="owner@example.com",
                phone="9999999999",
                created_at=datetime(2026, 4, 1, 12, 0, 0),
                role_id=2,
                role="USER",
            ),
        )

        self.assertEqual(result.order.status, "PAID")
        self.assertEqual(result.order.acc_no, 1234)
        self.assertEqual(result.order.total_amount, Decimal("2500.0"))
        self.assertIsNone(result.invoice)

    def test_pay_for_order_rejects_already_paid_order(self):
        connection = FakeConnection(
            [
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|ALREADY_PAID|409|Order has already been paid",
                    )
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            pay_for_order(
                connection,
                9,
                PayOrderRequest(acc_no=1234),
                AuthenticatedUser(
                    u_id=1,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "ALREADY_PAID")

    def test_pay_for_order_rejects_expired_account(self):
        connection = FakeConnection(
            [
                {
                    "execute_error": OperationalError(
                        1644,
                        "APP_ERROR|INVALID_ACCOUNT|400|Selected bank account is invalid",
                    )
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            pay_for_order(
                connection,
                9,
                PayOrderRequest(acc_no=1234),
                AuthenticatedUser(
                    u_id=1,
                    username="owner",
                    email="owner@example.com",
                    phone="9999999999",
                    created_at=datetime(2026, 4, 1, 12, 0, 0),
                    role_id=2,
                    role="USER",
                ),
            )

        self.assertEqual(context.exception.code, "INVALID_ACCOUNT")


if __name__ == "__main__":
    unittest.main()
