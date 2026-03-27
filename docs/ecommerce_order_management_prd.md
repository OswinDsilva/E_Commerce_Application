# Product Requirements Document (PRD)
# E-Commerce Order Management System

---

## 1. Overview

The system is a simplified e-commerce web application that allows users to browse products, add items to a cart, place orders, make payments, and generate invoices. It also includes an administrative interface for managing products and inventory.

The application integrates a PostgreSQL database with a backend API and supports real-world workflows such as order processing, payment handling, and inventory management.

---

## 2. Objectives

- Provide a functional e-commerce workflow from browsing to payment
- Demonstrate strong database design and integrity constraints
- Implement modular backend logic aligned with database procedures
- Handle inventory consistency and concurrent operations
- Support role-based access (User and Admin)

---

## 3. Scope

### In Scope

- User registration and authentication
- Product browsing and stock visibility
- Session-based cart functionality
- Order creation and validation
- Payment processing with bank accounts
- Invoice generation
- Inventory management
- Admin dashboard for product and stock management

### Out of Scope

- Persistent cart storage
- Multi-user sessions across devices
- Third-party payment gateway integration
- Advanced authentication (JWT, OAuth)
- Complex UI/UX design

---

## 4. User Roles

### 4.1 Customer (USER)

- Register and login
- Browse products
- Add items to cart
- Place orders
- Make payments
- View invoices

### 4.2 Admin (ADMIN)

- Add products
- Update product details
- Manage inventory levels

---

## 5. System Features

### 5.1 Authentication System

- Users can register with unique credentials
- Users can log in using username and password
- Role-based access is enforced (`USER` / `ADMIN`)

### 5.2 Product Marketplace

Displays all products with the following details:

| Field | Description |
|---|---|
| Name | Product name |
| Brand | Manufacturer or brand |
| Price | Unit price |
| Category | Product category |
| Stock Status | Availability indicator |

**Stock Status values:**

- `In Stock` — quantity > 0
- `Out of Stock` — quantity = 0

### 5.3 Cart System (Session-Based)

- Users can add products to a temporary cart
- Cart is stored in session (not database)
- Cart holds:
  - `product_id`
  - `quantity`

### 5.4 Order Management

Orders are created during checkout. Each order:

- Belongs to one user
- Contains one or more products
- Has a calculated total amount
- Maintains a status

**Order statuses:**

| Status | Description |
|---|---|
| `CREATED` | Order has been placed |
| `PAID` | Payment has been completed |

### 5.5 Payment System

- Users can pay for an order using a bank account
- Users can add and store bank account details
- Payment updates order status to `PAID`
- A user can only use their own bank account

### 5.6 Invoice Generation

- An invoice is generated after successful payment
- Each order has exactly one invoice
- Invoice includes:
  - Order details
  - Total amount
  - Billing address
  - Shipping address

### 5.7 Inventory Management

Each product has an associated inventory record that tracks:

- Quantity
- Last updated timestamp

### 5.8 Admin Dashboard

Admin users can:

- Add new products
- Update product details
- Modify inventory

---

## 6. System Workflow

### 6.1 Customer Flow

```
Register / Login
      ↓
Browse Products
      ↓
Add Items to Cart
      ↓
Proceed to Checkout
      ↓
System Validates Cart Items
      ↓
Order is Created → Inventory Updated
      ↓
User Makes Payment
      ↓
Invoice Generated
```

### 6.2 Admin Flow

```
Admin Logs In
      ↓
Access Dashboard
      ↓
Add / Update Products
      ↓
Update Inventory
```

---

## 7. Functional Requirements

### 7.1 User Management

- The system must allow user registration
- The system must ensure unique usernames and emails
- The system must support user authentication
- The system must allow user deletion

### 7.2 Product Management

- The system must allow creation of products
- The system must display all products
- The system must show stock status

### 7.3 Inventory Management

- The system must maintain inventory for each product
- The system must prevent negative stock values
- The system must update inventory after order placement

### 7.4 Order Management

- The system must create orders at checkout
- The system must validate product availability
- The system must ensure each order contains at least one item

### 7.5 Payment Processing

- The system must validate bank account ownership
- The system must update order status after payment
- The system must prevent duplicate payments

### 7.6 Invoice Management

- The system must generate an invoice after payment
- The system must enforce one invoice per order

---

## 8. Non-Functional Requirements

### 8.1 Performance

- System should handle multiple concurrent order requests
- Inventory updates must be efficient

### 8.2 Consistency

- Inventory must remain consistent under concurrent operations
- Orders must accurately reflect purchased items

### 8.3 Security

- Passwords must be stored securely (hashed)
- Users must not access unauthorized resources

### 8.4 Reliability

- Transactions must ensure data integrity
- Failures during order processing should not corrupt data

---

## 9. Data Integrity Constraints

- A user must exist before creating an order
- A bank account must belong to a valid user
- An order must contain at least one product
- Inventory cannot go below zero
- Each product must have exactly one inventory record
- Each order must have at most one invoice

---

## 10. Concurrency Handling

- The system must prevent overselling of products
- Inventory rows must be locked during updates
- Concurrent order operations must maintain consistency

---

## 11. Success Criteria

The project is considered successful if:

- Users can complete the full flow from login to invoice generation
- Inventory updates correctly after orders
- Payments correctly update order status
- Admin can manage products and inventory
- Data integrity is maintained across all operations

---

## 12. Summary

The system provides a complete e-commerce workflow while maintaining a strong focus on database integrity, modular design, and realistic business logic. It demonstrates key DBMS concepts including relational modeling, constraints, transactions, and concurrency control.
