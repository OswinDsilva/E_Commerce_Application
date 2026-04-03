# API Justification — Why Each Endpoint Exists

This document explains the business need behind each API group.

---

## 1. Auth (`/auth/*`)

**Why:** The system requires role-based access (`USER` vs `ADMIN`). Without authentication, users could impersonate others, place orders under false identities, or access the admin panel. Session-based auth enforces ownership throughout the order lifecycle.

**Key flows it enables:**
- Only the authenticated user can view their own orders and invoices
- Admin-only endpoints (`POST /products`, `PUT /inventory`) are gated behind role checks
- `GET /auth/me` lets the frontend restore session on page refresh without a login prompt

---

## 2. Users (`/users/*`)

**Why:** While users are identified by their session, a dedicated user endpoint allows profile inspection and account deletion. In the current Person 1 implementation, these endpoints are self-only and enforce ownership through the active session.

Deleting a user still relies on schema-level cascade behavior for related orders and bank accounts, but the API limits who can trigger that deletion.

---

## 3. Products (`/products/*`)

**Why:** The entire storefront depends on a live product listing. Fetching from the database (rather than a static file) ensures:
- Stock status (`In Stock` / `Out of Stock`) is always real-time
- Admin additions/updates are immediately visible
- Category filtering and search work server-side for large catalogs

---

## 4. Inventory (`/inventory/*`)

**Why:** Separated from products intentionally, mirroring the schema's weak-entity design. The inventory endpoint gives:
- Admins a dedicated surface to adjust stock without touching product metadata
- The order endpoint a clear integration point to check and decrement stock atomically

This separation prevents the classic "oversell" bug where concurrent reads return stale stock counts.

---

## 5. Categories (`/categories`)

**Why:** A simple lookup endpoint that keeps the frontend's filter UI in sync with the database. If a new category is added by an admin, the filter dropdown auto-updates without a frontend deploy.

---

## 6. Orders (`/orders/*`)

**Why:** The most critical API group, covering the complete order lifecycle:

Current implementation note: the Person 1 payment endpoint validates order ownership, validates bank account ownership, marks the order `PAID`, and returns invoice data only if an invoice already exists.

| Endpoint | Justification |
|----------|---------------|
| `POST /orders` | Creates the order record and **atomically validates + decrements** inventory in a single transaction, preventing overselling |
| `GET /orders` | Users need to track their purchase history |
| `GET /orders/:o_id` | Required for checkout confirmation and the invoice view |
| `POST /orders/:o_id/pay` | Validates order ownership, validates bank account ownership, marks the order `PAID`, and returns invoice data if one already exists |

---

## 7. Bank Accounts (`/bank-accounts/*`)

**Why:** The schema requires that each payment is linked to a verified bank account that belongs to the paying user. The frontend needs to:
- List accounts for the user to select during payment
- Allow adding new accounts in-session
- Prevent UI states where a user can attempt to pay with another user's account (enforced server-side too)

In the current implementation, bank account creation always binds the account to the authenticated user from the session rather than accepting a user ID from the request.

---

## 8. Invoices (`/invoices/*`)

**Why:** Per the PRD, every paid order generates exactly one invoice. Rather than recomputing invoice data on the fly, the invoice is stored and retrieved via this endpoint. This ensures:
- Invoices remain immutable even if product prices change later
- The print/download flow always reflects the price at the time of purchase (`price_at_purchase` from `ordered_items`)

