from datetime import date, datetime
from decimal import Decimal
import unittest

from backend.errors import ApiError
from backend.schemas.orders import OrderCreateRequest, OrderItemIn, OrderOut, OrderItemsUpdateRequest
from backend.schemas.users import AuthenticatedUser
from backend.services.order_service import (
    add_items_to_order,
    create_order,
    get_order_by_id,
    list_order_items,
    list_orders,
)


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.current_step = None

    def execute(self, query, params=None):
        if self.connection.step_index >= len(self.connection.steps):
            raise AssertionError(f"Unexpected query: {query!r} {params!r}")

        self.current_step = self.connection.steps[self.connection.step_index]
        self.connection.step_index += 1
        error = self.current_step.get("execute_error")
        if error is not None:
            raise error

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


def _test_user(u_id: int = 1, role: str = "USER") -> AuthenticatedUser:
    return AuthenticatedUser(
        u_id=u_id,
        username="owner",
        email="owner@example.com",
        phone="9999999999",
        created_at=datetime(2026, 4, 1, 12, 0, 0),
        role_id=2,
        role=role,
    )


class Person3OrderServiceTests(unittest.TestCase):
    def test_create_order_with_items_returns_created_order(self):
        connection = FakeConnection(
            [
                {
                    "fetchall": [
                        {
                            "o_id": 22,
                            "order_date": date(2026, 4, 8),
                            "status": "CREATED",
                            "total_amount": Decimal("0.00"),
                            "u_id": 1,
                            "acc_no": None,
                        }
                    ]
                },
            ]
        )

        order = create_order(
            connection,
            OrderCreateRequest(
                items=[OrderItemIn(p_id=1, quantity=2)],
                shipping_address="123 Demo Street",
                billing_address="123 Demo Street",
            ),
            _test_user(),
        )

        self.assertEqual(order.o_id, 22)
        self.assertEqual(order.status, "CREATED")
        self.assertEqual(order.total_amount, Decimal("0.00"))

    def test_get_order_by_id_rejects_other_user(self):
        connection = FakeConnection(
            [
                {
                    "fetchone": {
                        "o_id": 7,
                        "order_date": date(2026, 4, 8),
                        "status": "CREATED",
                        "total_amount": Decimal("100.00"),
                        "u_id": 99,
                        "acc_no": None,
                    }
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            get_order_by_id(connection, 7, _test_user(u_id=1))

        self.assertEqual(context.exception.code, "UNAUTHORIZED")

    def test_list_orders_returns_current_user_orders(self):
        connection = FakeConnection(
            [
                {
                    "fetchall": [
                        {
                            "o_id": 2,
                            "order_date": date(2026, 4, 8),
                            "status": "CREATED",
                            "total_amount": Decimal("50.00"),
                            "u_id": 1,
                            "acc_no": None,
                        },
                        {
                            "o_id": 1,
                            "order_date": date(2026, 4, 7),
                            "status": "PAID",
                            "total_amount": Decimal("20.00"),
                            "u_id": 1,
                            "acc_no": 1001,
                        },
                    ]
                }
            ]
        )

        orders = list_orders(connection, _test_user())

        self.assertEqual(len(orders), 2)
        self.assertIsInstance(orders[0], OrderOut)
        self.assertEqual(orders[0].o_id, 2)

    def test_add_items_to_order_returns_updated_order(self):
        connection = FakeConnection(
            [
                {
                    "fetchall": [
                        {
                            "o_id": 22,
                            "order_date": date(2026, 4, 8),
                            "status": "CREATED",
                            "total_amount": Decimal("120.00"),
                            "u_id": 1,
                            "acc_no": None,
                        }
                    ]
                }
            ]
        )

        updated = add_items_to_order(
            connection,
            22,
            OrderItemsUpdateRequest(items=[OrderItemIn(p_id=2, quantity=1)]),
            _test_user(),
        )

        self.assertEqual(updated.o_id, 22)
        self.assertEqual(updated.total_amount, Decimal("120.00"))

    def test_list_order_items_rejects_other_user(self):
        connection = FakeConnection(
            [
                {
                    "fetchone": {
                        "o_id": 22,
                        "order_date": date(2026, 4, 8),
                        "status": "CREATED",
                        "total_amount": Decimal("120.00"),
                        "u_id": 99,
                        "acc_no": None,
                    }
                }
            ]
        )

        with self.assertRaises(ApiError) as context:
            list_order_items(connection, 22, _test_user())

        self.assertEqual(context.exception.code, "UNAUTHORIZED")


if __name__ == "__main__":
    unittest.main()
