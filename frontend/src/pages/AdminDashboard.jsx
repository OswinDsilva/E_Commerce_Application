import React, { useState } from 'react'
import { Plus, Package, Archive, Edit3, Save, X, BarChart2 } from 'lucide-react'
import { PRODUCTS } from '../data/mockData'
import './AdminDashboard.css'

const TABS = ['Overview', 'Products', 'Inventory', 'Add Product']

export default function AdminDashboard() {
  const [tab, setTab] = useState('Overview')
  const [products, setProducts] = useState(PRODUCTS)
  const [editId, setEditId] = useState(null)
  const [editData, setEditData] = useState({})
  const [newProduct, setNewProduct] = useState({ product_name: '', brand: '', price: '', category_name: '', description: '', stock: '' })
  const [saved, setSaved] = useState(false)

  const handleEdit = (p) => { setEditId(p.p_id); setEditData({ ...p }) }
  const handleSave = () => {
    setProducts(ps => ps.map(p => p.p_id === editId ? { ...editData } : p))
    setEditId(null)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }
  const handleAddProduct = (e) => {
    e.preventDefault()
    const np = { ...newProduct, p_id: Date.now(), price: parseFloat(newProduct.price), stock: parseInt(newProduct.stock), category: 1, image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80' }
    setProducts(ps => [...ps, np])
    setNewProduct({ product_name: '', brand: '', price: '', category_name: '', description: '', stock: '' })
    setTab('Products')
  }

  const stats = [
    { label: 'Total Products', value: products.length, icon: <Package size={22} /> },
    { label: 'In Stock',       value: products.filter(p => p.stock > 0).length, icon: <Archive size={22} /> },
    { label: 'Out of Stock',   value: products.filter(p => p.stock === 0).length, icon: <BarChart2 size={22} /> },
    { label: 'Categories',     value: new Set(products.map(p => p.category)).size, icon: <BarChart2 size={22} /> },
  ]

  return (
    <div className="admin container">
      <div className="admin__header">
        <div>
          <p className="section-eyebrow">Admin</p>
          <h1>Dashboard</h1>
        </div>
        {saved && <span className="badge badge-success" style={{alignSelf:'center'}}>Changes saved!</span>}
      </div>

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
              {products.filter(p => p.stock < 5).map(p => (
                <div key={p.p_id} className="admin-low-item card">
                  <img src={p.image} alt={p.product_name} />
                  <div>
                    <p className="admin-low-item__name">{p.product_name}</p>
                    <p className="admin-low-item__stock">{p.stock === 0 ? 'Out of stock' : `${p.stock} remaining`}</p>
                  </div>
                  <span className={`badge ${p.stock === 0 ? 'badge-error' : 'badge-gold'}`}>{p.stock}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Products */}
      {tab === 'Products' && (
        <div className="animate-fadeIn">
          <table className="admin-table">
            <thead>
              <tr><th>Image</th><th>Name</th><th>Brand</th><th>Price</th><th>Category</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr key={p.p_id}>
                  <td><img src={p.image} alt={p.product_name} className="admin-table__thumb" /></td>
                  <td>{editId === p.p_id
                    ? <input className="input" value={editData.product_name} onChange={e => setEditData(d => ({...d, product_name: e.target.value}))} />
                    : p.product_name}</td>
                  <td>{editId === p.p_id
                    ? <input className="input" value={editData.brand} onChange={e => setEditData(d => ({...d, brand: e.target.value}))} />
                    : p.brand}</td>
                  <td>{editId === p.p_id
                    ? <input className="input" type="number" value={editData.price} onChange={e => setEditData(d => ({...d, price: parseFloat(e.target.value)}))} />
                    : `$${p.price.toLocaleString()}`}</td>
                  <td><span className="badge badge-neutral">{p.category_name}</span></td>
                  <td className="admin-table__actions">
                    {editId === p.p_id ? (
                      <>
                        <button className="btn btn-gold btn-sm" onClick={handleSave}><Save size={14} /> Save</button>
                        <button className="btn btn-ghost btn-sm" onClick={() => setEditId(null)}><X size={14} /></button>
                      </>
                    ) : (
                      <button className="btn btn-outline btn-sm" onClick={() => handleEdit(p)}><Edit3 size={14} /> Edit</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Inventory */}
      {tab === 'Inventory' && (
        <div className="animate-fadeIn">
          <table className="admin-table">
            <thead>
              <tr><th>Product</th><th>Current Stock</th><th>Status</th><th>Update Stock</th></tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr key={p.p_id}>
                  <td>{p.product_name}</td>
                  <td>{p.stock}</td>
                  <td><span className={`badge ${p.stock > 0 ? 'badge-success' : 'badge-error'}`}>{p.stock > 0 ? 'In Stock' : 'Out of Stock'}</span></td>
                  <td>
                    <input
                      className="input admin-stock-input"
                      type="number"
                      min="0"
                      defaultValue={p.stock}
                      onChange={e => setProducts(ps => ps.map(pr => pr.p_id === p.p_id ? { ...pr, stock: parseInt(e.target.value) || 0 } : pr))}
                      aria-label={`Stock for ${p.product_name}`}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Product */}
      {tab === 'Add Product' && (
        <div className="admin-add animate-fadeIn">
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
                <input id="np-category" className="input" value={newProduct.category_name} onChange={e => setNewProduct(p => ({...p, category_name: e.target.value}))} placeholder="e.g. Clothing" required />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="np-stock">Initial Stock</label>
                <input id="np-stock" className="input" type="number" min="0" value={newProduct.stock} onChange={e => setNewProduct(p => ({...p, stock: e.target.value}))} placeholder="0" required />
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
    </div>
  )
}
