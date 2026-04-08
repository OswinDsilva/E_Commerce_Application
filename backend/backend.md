# Backend Overview

The backend is implemented with FastAPI and organized so routing, business logic, and shared helpers stay separate.

## Current backend layout

- `main.py`
  - FastAPI application entrypoint
  - Registers routers and the shared API error handler
- `routers/`
  - HTTP route definitions for auth, users, bank accounts, and payments
- `services/`
  - Business logic for registration, login, user ownership checks, bank account management, and payment validation
- `utils/`
  - Shared helpers for password hashing, in-memory session handling, and auth guards
- `errors.py`
  - Shared `ApiError` type used for consistent API error responses
- `database.py`
  - MySQL connection and dependency helpers
- `config.py`
  - Environment variable loading and database URL parsing

## Person 1 module coverage

The current Person 1 backend implementation covers:

- user registration with password hashing and duplicate username/email checks
- login, logout, and current-session lookup
- self-only user profile access and account deletion
- bank account add/list/delete for the authenticated user
- payment ownership validation for `POST /orders/{o_id}/pay`

## Notes

- Session tracking is intentionally minimal and stored in memory.
- The payment endpoint validates order ownership, validates bank account ownership, and marks the order as `PAID`.
- Invoice creation is not implemented in the Person 1 module; the payment endpoint only returns invoice data if one already exists.
