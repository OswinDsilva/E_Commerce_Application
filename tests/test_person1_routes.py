from datetime import date, datetime
from decimal import Decimal
import unittest
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient
except RuntimeError:  # pragma: no cover - depends on optional test dependency
    TestClient = None

from backend.database import get_db
from backend.main import app
from backend.routers import bank_accounts, payments
from backend.schemas.bank_accounts import BankAccountOut
from backend.schemas.payments import OrderOut, PayOrderResponse
from backend.schemas.users import AuthenticatedUser


def _test_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        u_id=1,
        username="owner",
        email="owner@example.com",
        phone="9999999999",
        created_at=datetime(2026, 4, 1, 12, 0, 0),
        role_id=2,
        role="USER",
    )


@unittest.skipIf(TestClient is None, "httpx is required for route tests")
class Person1RouteModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        app.dependency_overrides[get_db] = lambda: object()

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_register_route_rejects_missing_email_with_pydantic_validation(self):
        response = self.client.post(
            "/auth/register",
            json={
                "username": "new-user",
                "password": "secret123",
                "phone": "9999999999",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("email", response.text)

    def test_auth_me_route_uses_user_response_wrapper(self):
        with patch("backend.routers.auth.require_auth", return_value=_test_user()):
            response = self.client.get("/auth/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "user": {
                    "u_id": 1,
                    "username": "owner",
                    "email": "owner@example.com",
                    "phone": "9999999999",
                    "created_at": "2026-04-01T12:00:00",
                    "role_id": 2,
                    "role": "USER",
                }
            },
        )

    def test_create_bank_account_route_keeps_response_shape(self):
        app.dependency_overrides[bank_accounts._current_user] = _test_user

        with patch(
            "backend.routers.bank_accounts.add_bank_account",
            return_value=BankAccountOut(
                acc_no=1234,
                bank_name="Demo Bank",
                expiry_date=date(2027, 5, 1),
                u_id=1,
            ),
        ):
            response = self.client.post(
                "/bank-accounts",
                json={
                    "acc_no": 1234,
                    "bank_name": "Demo Bank",
                    "expiry_date": "2027-05-01",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "account": {
                    "acc_no": 1234,
                    "bank_name": "Demo Bank",
                    "expiry_date": "2027-05-01",
                    "u_id": 1,
                }
            },
        )

    def test_pay_order_route_serializes_decimal_totals_as_numbers(self):
        app.dependency_overrides[payments._current_user] = _test_user

        with patch(
            "backend.routers.payments.pay_for_order",
            return_value=PayOrderResponse(
                order=OrderOut(
                    o_id=9,
                    order_date=date(2026, 4, 3),
                    status="PAID",
                    total_amount=Decimal("2500.00"),
                    u_id=1,
                    acc_no=1234,
                ),
                invoice=None,
            ),
        ):
            response = self.client.post("/orders/9/pay", json={"acc_no": 1234})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["order"]["status"], "PAID")
        self.assertEqual(payload["order"]["total_amount"], 2500.0)
        self.assertIsNone(payload["invoice"])


if __name__ == "__main__":
    unittest.main()
