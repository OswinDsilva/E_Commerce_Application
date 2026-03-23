# Work Distribution Plan

This document outlines the division of work among three team members for the E-Commerce system project. Each member is responsible for a specific module, ensuring clear ownership and minimal overlap.

## Person 1 - User and Payment Module

### Core Responsibility

Handle user lifecycle, authentication, and payment ownership.

### Work to Do

1. User Management
- Implement user registration logic.
- Implement login validation.
- Handle user deletion.
- Ensure username and email uniqueness.
- Store passwords securely (hashed).

2. Authentication Handling
- Validate user identity before allowing actions.
- Ensure protected operations are performed only by the correct user.
- Maintain simple session or user tracking (minimal implementation is sufficient).

3. Bank Account Management
- Allow users to add bank accounts.
- Ensure each bank account is linked to exactly one user.
- Prevent invalid user references.
- Maintain integrity of banking data.

4. Payment Handling
- Ensure only the correct user can pay for their order.
- Validate that the selected bank account belongs to that user.
- Update order state after successful payment.
- Prevent duplicate or invalid payments.

### Key Constraints to Enforce

- A bank account must belong to a valid user.
- A user cannot use another user's bank account.
- A payment can only be made for a valid order.
- A paid order should not be paid again.

## Person 2 - Product and Inventory Module

### Core Responsibility

Handle product catalog and inventory correctness.

### Work to Do

1. Product Management
- Add new products.
- Ensure product data integrity (for example, price >= 0).
- Maintain product listings.

2. Inventory Management
- Maintain stock levels for each product.
- Update stock when required.
- Ensure inventory exists for every product.
- Track last updated time.

3. Stock Validation
- Ensure stock never becomes negative.
- Validate stock availability before any deduction.
- Provide accurate stock status at all times.

4. Product Availability Logic
- Ensure products are always visible in the catalog.
- Display correct stock status:
	- quantity > 0 -> In Stock
	- quantity = 0 -> Out of Stock

### Key Constraints to Enforce
/
- Inventory must never go below 0.
- Every product must have exactly one inventory record.
- Stock updates must remain consistent under concurrent access.

## Person 3 - Order and Invoice Module

### Core Responsibility

Handle order lifecycle, validation, concurrency, and invoice generation.

### Work to Do

1. Order Creation and Validation
- Create orders linked to users.
- Ensure valid user references.
- Maintain correct order states.
- Prevent invalid order creation.

2. Order Item Handling
- Add products to orders.
- Validate product existence.
- Validate requested quantity.
- Ensure order always contains valid items.

3. Concurrency Handling
- Prevent race conditions during stock updates.
- Ensure multiple users cannot oversell the same product.
- Lock relevant data during updates.
- Maintain consistency under simultaneous operations.

4. Order Integrity
- Maintain correct total amount for each order.
- Ensure totals reflect actual items.
- Keep order data consistent after every modification.

5. Invoice Generation
- Generate invoice only for valid orders.
- Ensure one invoice per order.
- Copy correct order details into invoice.
- Maintain billing and shipping data.

### Key Constraints to Enforce

- An order must belong to a valid user.
- An order must contain at least one product.
- Stock must be validated before adding items.
- Concurrent operations must not break inventory consistency.
- Each order must have at most one invoice.

## Integration Notes

- Payment updates depend on valid orders and correct user ownership.
- Order operations depend on inventory availability and consistency.
- Inventory updates must remain correct under concurrent order operations.

## Summary

| Person | Responsibility |
| --- | --- |
| Person 1 | User management, authentication, and payments |
| Person 2 | Product catalog and inventory management |
| Person 3 | Order processing, concurrency handling, and invoice generation |