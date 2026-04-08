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
from backend.routers import orders, payments
from backend.schemas.payments import InvoiceOut, PayOrderResponse
from backend.schemas.orders import OrderItemOut, OrderListResponse, OrderOut
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
class Person3RouteModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        app.dependency_overrides[get_db] = lambda: object()
        app.dependency_overrides[orders._current_user] = _test_user
        app.dependency_overrides[payments._current_user] = _test_user

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_create_order_route_returns_order_wrapper(self):
        with patch(
            "backend.routers.orders.create_order",
            return_value=OrderOut(
                o_id=9,
                order_date=date(2026, 4, 8),
                status="CREATED",
                total_amount=Decimal("0.00"),
                u_id=1,
                acc_no=None,
            ),
        ):
            response = self.client.post(
                "/orders",
                json={
                    "items": [{"p_id": 1, "quantity": 2}],
                    "shipping_address": "123 Demo Street",
                    "billing_address": "123 Demo Street",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "order": {
                    "o_id": 9,
                    "order_date": "2026-04-08",
                    "status": "CREATED",
                    "total_amount": 0.0,
                    "u_id": 1,
                    "acc_no": None,
                }
            },
        )

    def test_get_order_route_returns_order_detail_wrapper(self):
        with patch(
            "backend.routers.orders.get_order_by_id",
            return_value=OrderOut(
                o_id=9,
                order_date=date(2026, 4, 8),
                status="CREATED",
                total_amount=Decimal("10.50"),
                u_id=1,
                acc_no=None,
            ),
        ), patch(
            "backend.routers.orders.list_order_items",
            return_value=[
                OrderItemOut(
                    p_id=1,
                    product_name="Sample Product",
                    quantity=2,
                    price_at_purchase=Decimal("5.25"),
                    line_total=Decimal("10.50"),
                )
            ],
        ):
            response = self.client.get("/orders/9")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["order"]["total_amount"], 10.5)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_list_orders_route_returns_orders_wrapper(self):
        with patch(
            "backend.routers.orders.list_orders",
            return_value=OrderListResponse(
                orders=[
                    OrderOut(
                        o_id=9,
                        order_date=date(2026, 4, 8),
                        status="CREATED",
                        total_amount=Decimal("10.00"),
                        u_id=1,
                        acc_no=None,
                    )
                ]
            ).orders,
        ):
            response = self.client.get("/orders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["orders"]), 1)

    def test_add_items_route_returns_order_wrapper(self):
        with patch(
            "backend.routers.orders.add_items_to_order",
            return_value=OrderOut(
                o_id=9,
                order_date=date(2026, 4, 8),
                status="CREATED",
                total_amount=Decimal("40.00"),
                u_id=1,
                acc_no=None,
            ),
        ):
            response = self.client.post("/orders/9/items", json={"items": [{"p_id": 2, "quantity": 3}]})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["order"]["total_amount"], 40.0)

    def test_get_invoice_route_returns_order_and_invoice(self):
        with patch(
            "backend.routers.payments.get_invoice_for_order",
            return_value=PayOrderResponse(
                order=OrderOut(
                    o_id=9,
                    order_date=date(2026, 4, 8),
                    status="PAID",
                    total_amount=Decimal("40.00"),
                    u_id=1,
                    acc_no=2001,
                ),
                invoice=InvoiceOut(
                    i_id=11,
                    invoice_date=date(2026, 4, 8),
                    total_amount=Decimal("40.00"),
                    shipping_address="123 Demo Street",
                    billing_address="123 Demo Street",
                    o_id=9,
                ),
            ),
        ):
            response = self.client.get("/orders/9/invoice")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["invoice"]["i_id"], 11)


if __name__ == "__main__":
    unittest.main()
