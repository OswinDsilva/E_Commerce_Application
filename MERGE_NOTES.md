# Integration Notes for feature-product-module Branch

**Updated:** April 6, 2026  
**Branch:** `feature-product-module`  
**Status:** Backend converted to pymysql, Frontend ready for integration

---

## 🔄 Major Changes Made

### Backend Architecture
- **Migration**: SQLAlchemy ORM → **pymysql** (raw SQL queries)
- **Rationale**: Alignment with teammates' branches (`oswin`, `setup/prakhyath-db-fix`)
- **Files Modified**:
  - `backend/database.py` - Now uses pymysql direct connections
  - `backend/products/crud.py` - All queries rewritten in SQL
  - `backend/products/routes.py` - Routes updated for Connection type
  - `backend/main.py` - Import path fixed for module structure
  - `backend/products/models.py` - No longer used (models removed)

### Database
- Database name: `ecommerce` (must be created in MySQL)
- Credentials: root / DBSProject@1 (from `.env`)
- Schema loaded from: `sql/schema.sql`

---

## ✅ What's Working

### Backend API Endpoints
- ✅ `GET /products/` - List all products (in-stock first)
- ✅ `GET /products/{p_id}` - Get single product
- ✅ `POST /products/` - Create product
- ✅ `PUT /products/{p_id}` - Update product
- ✅ `DELETE /products/{p_id}` - Soft delete product
- ✅ `PUT /products/{p_id}/inventory` - Update stock
- ✅ `POST /products/{p_id}/deduct` - Deduct inventory
- ✅ `GET /categories/` - List categories
- ✅ `POST /categories/` - Add category
- ✅ `GET /docs` - Interactive API documentation

### Database
- ✅ Products table with full CRUD
- ✅ Inventory management
- ✅ Categories support
- ✅ Soft-delete functionality (is_active flag)

---

## ⚠️ Required Changes for Merged Branches

### For `oswin` Branch (Design System)
When merging their documentation and design updates:
- Update frontend components to use new design system
- No backend conflicts expected

### For `setup/prakhyath-db-fix` Branch (Auth/Payments)
**CRITICAL**: Their code uses **pymysql** (same as current branch)
- ✅ Authentication module: `backend/routers/auth.py` - Ready to integrate
- ✅ User management: `backend/services/user_service.py` - Ready to integrate
- ✅ Payment module: `backend/routers/payments.py` - Ready to integrate
- ✅ Email/Sessions: `backend/utils/` - Ready to integrate

**Action**: Merge their `backend/routers/`, `backend/services/`, and `backend/utils/` folders directly
**Note**: This branch also has database tables for users, auth, payments - ensure schema is updated

---

## 🖥️ Frontend Integration

### Current Status
- Frontend at `frontend/` is using Vite
- Currently has mock data from `frontend/src/data/mockData.js`
- Uses React Router and Context API for state

### Required Frontend Changes

#### 1. API Base URL
In `frontend/src/` create or update environment file:
```javascript
// frontend/.env.local
VITE_API_URL=http://127.0.0.1:8000
```

#### 2. ProductList Component
**Location**: `frontend/src/pages/ProductsPage.jsx`  
**Change**: Replace mock data with API calls

```javascript
// BEFORE (using mockData)
import { mockData } from '../data/mockData';

// AFTER (using API)
useEffect(() => {
  fetch(`${import.meta.env.VITE_API_URL}/products/`)
    .then(res => res.json())
    .then(data => setProducts(data))
    .catch(err => console.error('Error fetching products:', err));
}, []);
```

#### 3. CartContext
**Location**: `frontend/src/context/CartContext.jsx`  
**Change**: Sync cart with backend inventory before checkout

#### 4. AuthContext (After Auth Integration)
**Location**: `frontend/src/context/AuthContext.jsx`  
**Add**: Login/Register endpoints
```javascript
const login = async (username, password) => {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include'
  });
  return res.json();
};
```

#### 5. CORS Configuration
**Status**: Backend CORS already allows:
- `http://localhost:3000` 
- `http://localhost:5173` (Vite dev server)

No frontend changes needed for CORS.

---

## 🚀 Setup & Running Instructions

### 1. Backend Setup
```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Database Setup
```bash
# Create database
mysql -u root -p ecommerce

# Load schema
mysql -u root -p ecommerce < sql/schema.sql
```

### 3. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```

---

## 📋 Checklist for Merging Branches

- [ ] **Backend**
  - [ ] Verify pymysql is installed: `pip install pymysql`
  - [ ] .env file has correct MySQL credentials
  - [ ] Database `ecommerce` created and schema loaded
  - [ ] Test `/products/` endpoint returns data
  - [ ] Test `/docs` shows all endpoints
  
- [ ] **Frontend**
  - [ ] Update API URL to backend in `.env.local` or component
  - [ ] Replace mock data with `fetch()` calls
  - [ ] Test ProductsPage loads products from backend
  - [ ] Test cart/inventory sync

- [ ] **Auth Integration** (when merging prakhyath branch)
  - [ ] Add auth routes to `backend/main.py`
  - [ ] Verify user/email tables created
  - [ ] Update AuthContext to use `/auth/login` endpoint
  - [ ] Test login/register flow

- [ ] **Merge Conflicts**
  - [ ] Resolve `backend/database.py` - use current pymysql version
  - [ ] Resolve `backend/main.py` - ensure all routers included
  - [ ] Resolve `requirements.txt` - merge all dependencies

---

## 🔗 API Documentation

Full interactive API docs available at:  
**`http://127.0.0.1:8000/docs`**

### Example Requests

#### Get all products
```bash
curl http://127.0.0.1:8000/products/
```

#### Get single product
```bash
curl http://127.0.0.1:8000/products/1
```

#### Create product
```bash
curl -X POST http://127.0.0.1:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "New Product",
    "brand": "Brand",
    "price": 99.99,
    "category": 1,
    "description": "Description",
    "quantity": 10
  }'
```

---

## ⚡ Known Issues & Workarounds

### Issue 1: SQLAlchemy models removed
- **Impact**: `backend/products/models.py` is minimal (not used)
- **Fix**: Keep it or delete - no impact on runtime (uses direct SQL)

### Issue 2: No automated migrations
- **Impact**: Schema changes require manual SQL updates
- **Fix**: Edit `sql/schema.sql` and re-run schema commands

### Issue 3: Password stored in database.py
- **Fix**: Move to `.env` and load via config (planned for next iteration)

---

## 📞 Integration Contact Points

- **Products/Inventory**: Your work (Yash) - `backend/products/`
- **Auth/Payments**: Prakhyath's work - `backend/routers/auth.py`, `backend/services/`
- **Design System**: Oswin's work - `design-system/`
- **Frontend Integration**: Coordinate with frontend team

---

## 🎯 Next Steps

1. **Merge from oswin**: Get latest design system docs
2. **Merge from prakhyath**: Add auth/payments routers
3. **Frontend update**: Connect all pages to backend APIs
4. **Testing**: End-to-end flow testing
5. **Deployment**: Move to production environment

---

**Last Updated**: April 6, 2026  
**Branch Owner**: Yash (feature-product-module)  
**Framework**: FastAPI + pymysql + React (Vite)
