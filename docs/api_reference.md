# The Atelier — API Reference

Base URL: `https://api.theatelier.com/api`
Auth: All protected routes require a session cookie (`Set-Cookie` on login).

---

## Auth

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `POST` | `/auth/register` | `{ username, password, email, phone }` | `{ user }` | Register a new user |
| `POST` | `/auth/login` | `{ username, password }` | `{ user }` | Login and set session cookie |
| `POST` | `/auth/logout` | — | `204` | Destroy session |
| `GET` | `/auth/me` | — | `{ user }` | Get current session user |

---

## Users

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `GET` | `/users/:u_id` | — | `{ user }` | Get user profile |
| `DELETE` | `/users/:u_id` | — | `204` | Delete user (own or admin) |

---

## Products

| Method | Endpoint | Query | Response | Description |
|--------|----------|-------|----------|-------------|
| `GET` | `/products` | `?category_id&search&sort` | `{ products[] }` | List all products with inventory |
| `GET` | `/products/:p_id` | — | `{ product, inventory }` | Get single product |
| `POST` | `/products` | `{ product_name, brand, price, category, description, initial_stock }` | `{ product }` | *(Admin)* Create product |
| `PUT` | `/products/:p_id` | `{ product_name?, brand?, price?, description? }` | `{ product }` | *(Admin)* Update product |

---

## Inventory

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `GET` | `/inventory/:p_id` | — | `{ inventory }` | Get stock for product |
| `PUT` | `/inventory/:p_id` | `{ quantity }` | `{ inventory }` | *(Admin)* Set stock level |

---

## Categories

| Method | Endpoint | Response | Description |
|--------|----------|----------|-------------|
| `GET` | `/categories` | `{ categories[] }` | List all categories |

---

## Orders

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `POST` | `/orders` | `{ items: [{ p_id, quantity }], shipping_address, billing_address }` | `{ order }` | Create order, deduct inventory |
| `GET` | `/orders` | — | `{ orders[] }` | Get current user's orders |
| `GET` | `/orders/:o_id` | — | `{ order, items[] }` | Get order detail with line items |
| `POST` | `/orders/:o_id/pay` | `{ acc_no }` | `{ order, invoice }` | Pay for order, generate invoice |

---

## Bank Accounts

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `GET` | `/bank-accounts` | — | `{ accounts[] }` | Get own bank accounts |
| `POST` | `/bank-accounts` | `{ acc_no, bank_name, expiry_date }` | `{ account }` | Add bank account |
| `DELETE` | `/bank-accounts/:acc_no` | — | `204` | Remove bank account |

---

## Invoices

| Method | Endpoint | Response | Description |
|--------|----------|----------|-------------|
| `GET` | `/invoices/:o_id` | `{ invoice, order, items[] }` | Get invoice by order ID |

---

## Error Format

```json
{ "error": "Human-readable message", "code": "MACHINE_CODE" }
```

Common codes: `UNAUTHORIZED`, `NOT_FOUND`, `OUT_OF_STOCK`, `ALREADY_PAID`, `INVALID_ACCOUNT`
