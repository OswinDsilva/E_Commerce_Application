import React, { useState, useEffect } from 'react'
import { Plus, Package, Archive, Edit3, Save, X, BarChart2 } from 'lucide-react'
import {
  listProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  updateProductInventory,
  listCategories,
  createCategory,
  isBackendUnavailableError,
  getUserFacingErrorMessage,
} from '../services/api'
import { PRODUCTS, CATEGORIES } from '../data/mockData'
import './AdminDashboard.css'

const TABS = ['Overview', 'Products', 'Inventory', 'Add Product', 'Add Category']

const DEFAULT_NEW_PRODUCT = {
  product_name: '',
  brand: '',
  price: '',
  category_id: 1,
  description: '',
  quantity: '',
}

const normalizeProduct = (product, categoryMap = new Map()) => {
  const categoryId = Number(product.category_id ?? product.category ?? 0)
  return {
    ...product,
    category_id: categoryId,
    category_name: product.category_name || categoryMap.get(categoryId) || 'Uncategorized',
    quantity: Number(product.quantity ?? product.stock ?? 0),
    price: Number(product.price ?? 0),
  }
}

export default function AdminDashboard() {
  const [tab, setTab] = useState('Overview')
  const [products, setProducts] = useState(PRODUCTS)
  const [categories, setCategories] = useState(CATEGORIES)
  const [loading, setLoading] = useState(true)
  const [categoriesLoading, setCategoriesLoading] = useState(true)
  const [editId, setEditId] = useState(null)
  const [editData, setEditData] = useState({})
  const [newProduct, setNewProduct] = useState(DEFAULT_NEW_PRODUCT)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [saved, setSaved] = useState(false)
  const [savedMessage, setSavedMessage] = useState('Changes saved!')
  const [error, setError] = useState(null)
  const [categoryError, setCategoryError] = useState(null)
  const [addError, setAddError] = useState(null)
  const [addCategoryError, setAddCategoryError] = useState(null)
  const [usingProductFallback, setUsingProductFallback] = useState(false)
  const [usingCategoryFallback, setUsingCategoryFallback] = useState(false)

  const showSaved = (message = 'Changes saved!') => {
    setSavedMessage(message)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const loadCategories = async () => {
    setCategoriesLoading(true)
    setCategoryError(null)

    try {
      const data = await listCategories()
      setCategories(data)
      setNewProduct(prev => ({
        ...prev,
        category_id: data.some(c => Number(c.id) === Number(prev.category_id)) ? prev.category_id : (data[0]?.id || 1),
      }))
      setUsingCategoryFallback(false)
      return data
    } catch (err) {
      if (isBackendUnavailableError(err)) {
        setCategories(CATEGORIES)
        setNewProduct(prev => ({
          ...prev,
          category_id: CATEGORIES.some(c => Number(c.id) === Number(prev.category_id)) ? prev.category_id : (CATEGORIES[0]?.id || 1),
        }))
        setUsingCategoryFallback(true)
        return CATEGORIES
      }
      setCategoryError(getUserFacingErrorMessage(err, 'categoryList'))
      return categories
    } finally {
      setCategoriesLoading(false)
    }
  }

  const loadProducts = async (categorySource = categories) => {
    setLoading(true)
    setError(null)

    const categoryMap = new Map((categorySource || []).map(c => [Number(c.id), c.category]))
    try {
      const data = await listProducts()
      setProducts(data.map(product => normalizeProduct(product, categoryMap)))
      setUsingProductFallback(false)
    } catch (err) {
      if (isBackendUnavailableError(err)) {
        setProducts(PRODUCTS.map(product => normalizeProduct(product, categoryMap)))
        setUsingProductFallback(true)
      } else {
        setError(getUserFacingErrorMessage(err, 'productsList'))
      }
    } finally {
      setLoading(false)
    }
  }

  const categoryNameById = (categoryId) => {
    const id = Number(categoryId)
    return categories.find(c => Number(c.id) === id)?.category || 'Uncategorized'
  }

  // Fetch products on mount
  useEffect(() => {
    const initializeDashboard = async () => {
      const loadedCategories = await loadCategories()
      await loadProducts(loadedCategories)
    }

    initializeDashboard()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleEdit = (p) => { setEditId(p.p_id); setEditData({ ...p }) }
  
  const handleSave = async () => {
    try {
      const updated = await updateProduct(editId, {
        product_name: editData.product_name,
        brand: editData.brand,
        price: editData.price,
        category_id: editData.category_id,
        description: editData.description,
      })
      setProducts(ps => ps.map(p => p.p_id === editId ? normalizeProduct(updated, new Map(categories.map(c => [Number(c.id), c.category]))) : p))
      setEditId(null)
      showSaved()
    } catch (err) {
      setError(getUserFacingErrorMessage(err, 'productUpdate'))
    }
  }

  const handleAddProduct = async (e) => {
    e.preventDefault()
    setAddError(null)

    const categoryExists = categories.some(c => Number(c.id) === Number(newProduct.category_id))
    if (!newProduct.category_id || !categoryExists) {
      setAddError('Please select a valid category before adding the product.')
      return
    }

    try {
      const np = await createProduct({
        product_name: newProduct.product_name,
        brand: newProduct.brand,
        price: parseFloat(newProduct.price),
        category_id: newProduct.category_id,
        description: newProduct.description,
        quantity: parseInt(newProduct.quantity) || 0,
      })
      setProducts(ps => [...ps, normalizeProduct(np, new Map(categories.map(c => [Number(c.id), c.category])))])
      setNewProduct({ ...DEFAULT_NEW_PRODUCT, category_id: categories[0]?.id || 1 })
      setTab('Products')
      showSaved('Product added successfully!')
    } catch (err) {
      setAddError(getUserFacingErrorMessage(err, 'productCreate'))
    }
  }

  const handleAddCategory = async (e) => {
    e.preventDefault()
    setAddCategoryError(null)

    const cleaned = newCategoryName.trim()
    if (!cleaned) {
      setAddCategoryError('Category name cannot be empty.')
      return
    }

    try {
      const created = await createCategory(cleaned)
      setCategories(cs => {
        const next = [...cs, created]
        next.sort((a, b) => Number(a.id) - Number(b.id))
        return next
      })
      setNewCategoryName('')
      showSaved('Category added successfully!')
    } catch (err) {
      setAddCategoryError(getUserFacingErrorMessage(err, 'categoryCreate'))
    }
  }

  const handleDeleteProduct = async (p_id) => {
    if (confirm('Are you sure you want to delete this product?')) {
      try {
        await deleteProduct(p_id)
        setProducts(ps => ps.filter(p => p.p_id !== p_id))
        showSaved('Product deleted successfully!')
      } catch (err) {
        setError(getUserFacingErrorMessage(err, 'productDelete'))
      }
    }
  }

  const handleInventoryUpdate = async (p_id, newQuantity) => {
    try {
      const updated = await updateProductInventory(p_id, newQuantity)
      setProducts(ps => ps.map(p => p.p_id === p_id ? normalizeProduct(updated, new Map(categories.map(c => [Number(c.id), c.category]))) : p))
      showSaved('Inventory updated!')
    } catch (err) {
      setError(getUserFacingErrorMessage(err, 'productUpdate'))
    }
  }

  const stats = [
    { label: 'Total Products', value: products.length, icon: <Package size={22} /> },
    { label: 'In Stock',       value: products.filter(p => p.quantity > 0).length, icon: <Archive size={22} /> },
    { label: 'Out of Stock',   value: products.filter(p => p.quantity === 0).length, icon: <BarChart2 size={22} /> },
    { label: 'Categories',     value: categories.length, icon: <BarChart2 size={22} /> },
  ]

  return (
    <div className="admin container">
      <div className="admin__header">
        <div>
          <p className="section-eyebrow">Admin</p>
          <h1>Dashboard</h1>
        </div>
        {saved && <span className="badge badge-success" style={{alignSelf:'center'}}>{savedMessage}</span>}
      </div>

      {(usingProductFallback || usingCategoryFallback) && (
        <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
          Backend is unavailable. You are currently viewing fallback data.
        </div>
      )}

      {/* Tabs */}
      <div className="admin__tabs">
        {TABS.map(t => (
          <button key={t} className={`admin__tab ${tab === t ? 'admin__tab--active' : ''}`} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      {/* Overview */}
      {tab === 'Overview' && (
        <div className="admin__overview animate-fadeIn">
          <div className="admin-stats">
            {stats.map(s => (
              <div key={s.label} className="admin-stat card">
                <div className="admin-stat__icon">{s.icon}</div>
                <div>
                  <p className="admin-stat__value">{s.value}</p>
                  <p className="admin-stat__label">{s.label}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="admin-low-stock">
            <h3>Low Stock Alert</h3>
            <div className="admin-low-list">
              {products.filter(p => p.quantity < 5).map(p => (
                <div key={p.p_id} className="admin-low-item card">
                  <div>
                    <p className="admin-low-item__name">{p.product_name}</p>
                    <p className="admin-low-item__stock">{p.quantity === 0 ? 'Out of stock' : `${p.quantity} remaining`}</p>
                  </div>
                  <span className={`badge ${p.quantity === 0 ? 'badge-error' : 'badge-gold'}`}>{p.quantity}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Products */}
      {tab === 'Products' && (
        <div className="animate-fadeIn">
          {error && (
            <div className="alert alert-error admin-alert" style={{ marginBottom: '1rem' }}>
              <span>{error}</span>
              <div className="admin-alert__actions">
                <button className="btn btn-ghost btn-sm" onClick={() => loadProducts(categories)}>Retry</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setError(null)}>Dismiss</button>
              </div>
            </div>
          )}
          {loading ? (
            <p>Loading products...</p>
          ) : products.length === 0 ? (
            <div className="alert alert-warning">No products found yet. Use the Add Product tab to create your first item.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr><th>Name</th><th>Brand</th><th>Price</th><th>Category</th><th>Quantity</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.p_id}>
                    <td>{editId === p.p_id
                      ? <input className="input" value={editData.product_name} onChange={e => setEditData(d => ({...d, product_name: e.target.value}))} />
                      : p.product_name}</td>
                    <td>{editId === p.p_id
                      ? <input className="input" value={editData.brand} onChange={e => setEditData(d => ({...d, brand: e.target.value}))} />
                      : p.brand}</td>
                    <td>{editId === p.p_id
                      ? <input className="input" type="number" step="0.01" value={editData.price} onChange={e => setEditData(d => ({...d, price: parseFloat(e.target.value)}))} />
                      : `$${p.price.toLocaleString()}`}</td>
                    <td><span className="badge badge-neutral">{p.category_name || categoryNameById(p.category_id)}</span></td>
                    <td>{p.quantity}</td>
                    <td className="admin-table__actions">
                      {editId === p.p_id ? (
                        <>
                          <button className="btn btn-gold btn-sm" onClick={handleSave}><Save size={14} /> Save</button>
                          <button className="btn btn-ghost btn-sm" onClick={() => setEditId(null)}><X size={14} /></button>
                        </>
                      ) : (
                        <>
                          <button className="btn btn-outline btn-sm" onClick={() => handleEdit(p)}><Edit3 size={14} /> Edit</button>
                          <button className="btn btn-error btn-sm" onClick={() => handleDeleteProduct(p.p_id)}>Delete</button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Inventory */}
      {tab === 'Inventory' && (
        <div className="animate-fadeIn">
          {error && (
            <div className="alert alert-error admin-alert" style={{ marginBottom: '1rem' }}>
              <span>{error}</span>
              <div className="admin-alert__actions">
                <button className="btn btn-ghost btn-sm" onClick={() => loadProducts(categories)}>Retry</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setError(null)}>Dismiss</button>
              </div>
            </div>
          )}
          {loading ? (
            <p>Loading inventory...</p>
          ) : products.length === 0 ? (
            <div className="alert alert-warning">No inventory records available yet.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr><th>Product</th><th>Current Stock</th><th>Status</th><th>Update Stock</th></tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.p_id}>
                    <td>{p.product_name}</td>
                    <td>{p.quantity}</td>
                    <td><span className={`badge ${p.quantity > 0 ? 'badge-success' : 'badge-error'}`}>{p.quantity > 0 ? 'In Stock' : 'Out of Stock'}</span></td>
                    <td>
                      <input
                        className="input admin-stock-input"
                        type="number"
                        min="0"
                        defaultValue={p.quantity}
                        onBlur={e => {
                          const newQty = parseInt(e.target.value) || 0
                          if (newQty !== p.quantity) {
                            handleInventoryUpdate(p.p_id, newQty)
                          }
                        }}
                        aria-label={`Stock for ${p.product_name}`}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Add Product */}
      {tab === 'Add Product' && (
        <div className="admin-add animate-fadeIn">
          {categoryError && (
            <div className="alert alert-error admin-alert" style={{ marginBottom: '1rem', width: '100%', maxWidth: '700px' }}>
              <span>{categoryError}</span>
              <div className="admin-alert__actions">
                <button className="btn btn-ghost btn-sm" onClick={loadCategories}>Retry</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setCategoryError(null)}>Dismiss</button>
              </div>
            </div>
          )}
          {addError && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{addError}</div>}
          <form onSubmit={handleAddProduct} className="admin-add-form glass-card">
            <h3>Add New Product</h3>
            <div className="admin-add-grid">
              <div className="input-group">
                <label className="input-label" htmlFor="np-name">Product Name</label>
                <input id="np-name" className="input" value={newProduct.product_name} onChange={e => setNewProduct(p => ({...p, product_name: e.target.value}))} placeholder="e.g. Obsidian Overcoat" required />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="np-brand">Brand</label>
                <input id="np-brand" className="input" value={newProduct.brand} onChange={e => setNewProduct(p => ({...p, brand: e.target.value}))} placeholder="e.g. Maison Noir" required />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="np-price">Price (USD)</label>
                <input id="np-price" className="input" type="number" step="0.01" min="0" value={newProduct.price} onChange={e => setNewProduct(p => ({...p, price: e.target.value}))} placeholder="0.00" required />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="np-category">Category</label>
                <select
                  id="np-category"
                  className="input"
                  value={newProduct.category_id}
                  onChange={e => setNewProduct(p => ({ ...p, category_id: parseInt(e.target.value) }))}
                  disabled={categoriesLoading || categories.length === 0}
                  required
                >
                  {categories.length === 0 ? (
                    <option value="">No categories available</option>
                  ) : (
                    categories.map(c => (
                      <option key={c.id} value={c.id}>{c.category}</option>
                    ))
                  )}
                </select>
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="np-quantity">Initial Stock</label>
                <input id="np-quantity" className="input" type="number" min="0" value={newProduct.quantity} onChange={e => setNewProduct(p => ({...p, quantity: e.target.value}))} placeholder="0" required />
              </div>
            </div>
            <div className="input-group">
              <label className="input-label" htmlFor="np-desc">Description</label>
              <textarea id="np-desc" className="input" rows={3} value={newProduct.description} onChange={e => setNewProduct(p => ({...p, description: e.target.value}))} placeholder="Product description…" required />
            </div>
            <button type="submit" className="btn btn-primary btn-lg">
              <Plus size={18} /> Add Product
            </button>
          </form>
        </div>
      )}

      {/* Add Category */}
      {tab === 'Add Category' && (
        <div className="admin-add animate-fadeIn">
          {addCategoryError && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{addCategoryError}</div>}
          <form onSubmit={handleAddCategory} className="admin-add-form glass-card">
            <h3>Add New Category</h3>
            <div className="admin-add-grid admin-add-grid--single">
              <div className="input-group">
                <label className="input-label" htmlFor="nc-name">Category Name</label>
                <input
                  id="nc-name"
                  className="input"
                  value={newCategoryName}
                  onChange={e => setNewCategoryName(e.target.value)}
                  placeholder="e.g. Outerwear"
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-lg">
              <Plus size={18} /> Add Category
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
