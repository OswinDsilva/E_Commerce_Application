# Software Requirements Specification (SRS)
# E-Commerce Order Management System

---

## 1. Introduction

### 1.1 Purpose

This document provides a detailed description of the functional and non-functional requirements for the E-Commerce Order Management System. It serves as a reference for developers, reviewers, and evaluators to understand system behavior and constraints.

### 1.2 Scope

The system enables users to:

- Register and authenticate
- Browse products
- Add items to a session-based cart
- Place orders
- Make payments using bank accounts
- Generate invoices

Additionally, administrators can manage products and inventory.

### 1.3 Definitions

| Term | Definition |
|---|---|
| **User** | A registered customer of the system |
| **Admin** | A privileged user who manages products and inventory |
| **Cart** | Temporary session-based storage of selected items |
| **Order** | A finalized collection of items for purchase |
| **Invoice** | A billing document generated after payment |

---

## 2. Overall Description

### 2.1 System Perspective

The system follows a three-tier architecture:

```
Frontend (UI)
      ↓
Backend (FastAPI)
      ↓
PostgreSQL Database
```

### 2.2 System Functions

The system performs the following major functions:

- User authentication and management
- Product display and stock tracking
- Order creation and validation
- Payment processing
- Invoice generation
- Inventory management

### 2.3 User Classes

| Role | Capabilities |
|---|---|
| **Customer** (`USER`) | Can browse, order, and pay |
| **Administrator** (`ADMIN`) | Can manage products and inventory |

### 2.4 Assumptions

- Users access the system via a web interface
- Cart is session-based and not persistent
- Payments are simulated (no external gateway)

---

## 3. Functional Requirements

### 3.1 User Management

- The system shall allow users to register
- The system shall enforce unique usernames and emails
- The system shall allow users to log in
- The system shall store passwords securely
- The system shall allow users to delete their accounts

### 3.2 Authentication

- The system shall validate user credentials before granting access
- The system shall restrict admin features to `ADMIN` users only

### 3.3 Product Management

- The system shall allow admins to add products
- The system shall allow admins to update products
- The system shall display all products to users

### 3.4 Inventory Management

- The system shall maintain inventory for each product
- The system shall prevent inventory from becoming negative
- The system shall update inventory when orders are placed

### 3.5 Cart Management

- The system shall allow users to add items to a cart
- The system shall store the cart in session
- The system shall allow modification of cart items

### 3.6 Order Management

- The system shall create an order at checkout
- The system shall validate product availability before order creation
- The system shall ensure orders contain at least one product

### 3.7 Payment Processing

- The system shall allow users to select or add bank accounts
- The system shall verify that the bank account belongs to the user
- The system shall update order status upon successful payment
- The system shall prevent duplicate payments

### 3.8 Invoice Generation

- The system shall generate an invoice after successful payment
- The system shall ensure one invoice per order

---

## 4. Non-Functional Requirements

### 4.1 Performance

- The system shall handle multiple concurrent users
- Inventory updates shall be efficient

### 4.2 Reliability

- The system shall maintain data integrity during transactions
- Failures shall not corrupt database state

### 4.3 Security

- Passwords shall be stored securely (hashed)
- Users shall not access unauthorized features

### 4.4 Scalability

- The system should support increasing numbers of users and products

---

## 5. External Interface Requirements

### 5.1 User Interface

The system shall provide pages for:

- Login / Register
- Product listing
- Cart
- Payment
- Invoice
- Admin dashboard

### 5.2 Database Interface

- The backend shall interact with PostgreSQL
- All critical operations shall maintain referential integrity

---

## 6. Data Requirements

### 6.1 Entities

- Users
- Bank Accounts
- Products
- Inventory
- Orders
- Ordered Items
- Invoice

### 6.2 Data Constraints

- A user must exist before creating an order
- A bank account must belong to a user
- Inventory must not be negative
- Each order must have at most one invoice

---

## 7. Concurrency Requirements

- The system shall prevent overselling of products
- Inventory updates shall use locking mechanisms
- Concurrent order processing shall maintain consistency

---

## 8. System Workflow

### 8.1 Order Flow

```
Cart → Validate → Create Order → Update Inventory → Payment → Invoice
```

### 8.2 Admin Flow

```
Admin Login → Add / Update Product → Update Inventory
```

---

## 9. Constraints

- The system uses **PostgreSQL** as the database
- Backend is implemented using **FastAPI**
- Cart is session-based and not persistent

---

## 10. Acceptance Criteria

The system is accepted if:

- Users can complete the full purchase flow
- Inventory updates correctly after orders
- Payments correctly update order status
- Invoice is generated after payment
- Admin can manage products and inventory

---

## 11. System Architecture Description

### 11.1 High-Level Architecture

```
Frontend (HTML/JS)
        ↓
FastAPI Backend
        ↓
PostgreSQL Database
```

### 11.2 Component Responsibilities

| Component | Responsibility |
|---|---|
| **Frontend** | User interaction |
| **Backend** | Business logic and API |
| **Database** | Data storage and integrity |

---

## 12. Summary

This system demonstrates a complete e-commerce workflow while emphasizing database design, integrity, and concurrency handling. It provides a modular and scalable structure suitable for academic evaluation and practical implementation.
