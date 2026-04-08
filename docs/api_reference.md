# The Atelier — API Reference

Base URL: `https://api.theatelier.com/api`
Auth: All protected routes require a session cookie (`Set-Cookie` on login).
Current implementation note: the Person 1 backend currently implements auth, users, bank accounts, and payment ownership checks.

---

## Auth

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `POST` | `/auth/register` | `{ username, password, email, phone }` | `201 { user }` | Register a new user, create a session, and set a session cookie |
| `POST` | `/auth/login` | `{ username, password }` | `{ user }` | Login and set session cookie |
| `POST` | `/auth/logout` | — | `204` | Destroy session |
| `GET` | `/auth/me` | — | `{ user }` | Get current session user |

---

## Users

Current implementation note: these endpoints are self-only in the current Person 1 backend.

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `GET` | `/users/:u_id` | — | `{ user }` | Get own user profile |
| `DELETE` | `/users/:u_id` | — | `204` | Delete own user account |

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
| `POST` | `/orders/:o_id/pay` | `{ acc_no }` | `{ order, invoice }` | Validate ownership, mark the order as `PAID`, and return invoice data if it already exists |

---

## Bank Accounts

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `GET` | `/bank-accounts` | — | `{ accounts[] }` | Get own bank accounts |
| `POST` | `/bank-accounts` | `{ acc_no, bank_name, expiry_date }` | `201 { account }` | Add a bank account for the authenticated user |
| `DELETE` | `/bank-accounts/:acc_no` | — | `204` | Remove bank account |

---

## Invoices

| Method | Endpoint | Response | Description |
|--------|----------|----------|-------------|
| `GET` | `/orders/:o_id/invoice` | `{ order, invoice }` | Get generated invoice for an order |

---

## Error Format

```json
{ "error": "Human-readable message", "code": "MACHINE_CODE" }
```

Common codes: `UNAUTHORIZED`, `NOT_FOUND`, `OUT_OF_STOCK`, `ALREADY_PAID`, `INVALID_ACCOUNT`, `BAD_REQUEST`

