# Data Flow Diagram (DFD)
# E-Commerce Order Management System

---

## 1. Level 0 DFD (Context Diagram)

### Description

The Level 0 DFD represents the entire system as a single process interacting with external entities.

### External Entities

- User (Customer)
- Admin
- Database (MySQL)

### Main Process

- E-Commerce System

### Data Flows

**From User → System**
- Registration details
- Login credentials
- Product requests
- Cart actions
- Order requests
- Payment details

**From System → User**
- Authentication response
- Product list
- Order confirmation
- Invoice details

**From Admin → System**
- Product data
- Inventory updates

**From System → Admin**
- Product status
- Inventory status

### Diagram

```
User ───────▶ E-Commerce System ───────▶ Database
  ▲                │                        │
  │                ▼                        ▼
  ◀──────────── System Responses ◀─────────

Admin ───────▶ System (Manage Products/Inventory)
```

---

## 2. Level 1 DFD (Detailed Diagram)

### Processes

| # | Process | Responsibilities |
|---|---|---|
| 1 | **User Management** | Registration, Login, Authentication |
| 2 | **Product & Inventory Management** | Product retrieval, Inventory updates, Stock validation |
| 3 | **Cart Management** *(Session-Based)* | Add/remove items, Temporary cart storage |
| 4 | **Order Processing** | Order creation, Item validation, Total calculation |
| 5 | **Payment Processing** | Bank account validation, Payment completion, Order status update |
| 6 | **Invoice Generation** | Invoice creation, Order-to-invoice mapping |

### Data Stores

- Users
- Bank Accounts
- Products
- Inventory
- Orders
- Ordered Items
- Invoice

### Data Flow Breakdown

| Flow | Direction | Data |
|---|---|---|
| User → User Management | Input | Registration data, Login credentials |
| User → Product System | Input | Product browsing request |
| Product System → User | Output | Product list with stock status |
| User → Cart | Input | Add/remove items |
| Cart → Order Processing | Internal | Selected items |
| Order Processing → Inventory | Query | Stock validation request |
| Inventory → Order Processing | Response | Stock availability |
| Order Processing → Database | Write | Store order, Store ordered items |
| User → Payment Processing | Input | Bank account details |
| Payment Processing → Database | Write | Update order status, Store bank account |
| Payment Processing → Invoice | Trigger | Trigger invoice generation |
| Invoice → Database | Write | Store invoice |
| Invoice → User | Output | Display invoice |

### Diagram

```
User
 │
 ▼
[User Management] ───────────▶ Users DB
 │
 ▼
[Product & Inventory] ───────▶ Products DB
 │                              Inventory DB
 ▼
[Cart (Session)]
 │
 ▼
[Order Processing] ─────────▶ Orders DB
 │                             Ordered_Items DB
 ▼
[Payment Processing] ───────▶ Bank_Account DB
 │                             Orders DB
 ▼
[Invoice Generation] ───────▶ Invoice DB
 │
 ▼
User (Invoice Output)
```

---

## 3. How to Draw This (For Submission)

### Level 0 Diagram

Draw one big process — **E-Commerce System** — with two external entities: **User** and **Admin**.

Show arrows for:
- **Inputs**: login, orders, payment
- **Outputs**: invoice, product list

### Level 1 Diagram

Draw 6 processes:

1. User Management
2. Product & Inventory
3. Cart
4. Order Processing
5. Payment Processing
6. Invoice Generation

Add:
- Data stores (open-ended rectangles)
- Arrows showing the flow between processes

---

## 4. Key Points for Viva

**Q: Why separate processes?**

> Each process represents a logical module of the system, ensuring modularity, clarity, and separation of concerns.

**Q: Why is cart not a data store?**

> The cart is session-based and temporary, so it is not persisted in the database and is not represented as a data store.

**Q: Where is concurrency handled?**

> Concurrency is handled in the **Order Processing** and **Inventory** modules, where stock validation and updates occur with locking mechanisms.

---

## 5. Summary

The DFD shows:

- Clear separation of modules
- Proper data movement across the system
- Database interaction points for each module
- A realistic end-to-end workflow representation
