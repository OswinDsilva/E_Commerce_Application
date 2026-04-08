import React, { useState, useEffect, useMemo } from 'react'
import { Search, SlidersHorizontal, X } from 'lucide-react'
import { listProducts, listCategories, isBackendUnavailableError, getUserFacingErrorMessage } from '../services/api'
import { PRODUCTS, CATEGORIES } from '../data/mockData'
import ProductCard from '../components/ProductCard'
import './ProductsPage.css'

export default function ProductsPage() {
  const [search, setSearch] = useState('')
  const [selectedCat, setSelectedCat] = useState(0)
  const [sortBy, setSortBy] = useState('default')
  const [showFilters, setShowFilters] = useState(false)
  const [products, setProducts] = useState(PRODUCTS)
  const [categories, setCategories] = useState(CATEGORIES)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const [productsData, categoriesData] = await Promise.all([
          listProducts(),
          listCategories(),
        ])
        setProducts(productsData)
        setCategories(categoriesData)
      } catch (err) {
        if (isBackendUnavailableError(err)) {
          // Fallback to mock data
          setProducts(PRODUCTS)
          setCategories(CATEGORIES)
        } else {
          setError(getUserFacingErrorMessage(err, 'productsList'))
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const filtered = useMemo(() => {
    let list = [...products]
    if (search) list = list.filter(p => p.product_name.toLowerCase().includes(search.toLowerCase()) || p.brand.toLowerCase().includes(search.toLowerCase()))
    if (selectedCat) list = list.filter(p => p.category_id === selectedCat)
    if (sortBy === 'price-asc')  list.sort((a,b) => a.price - b.price)
    if (sortBy === 'price-desc') list.sort((a,b) => b.price - a.price)
    if (sortBy === 'name')       list.sort((a,b) => a.product_name.localeCompare(b.product_name))
    return list
  }, [search, selectedCat, sortBy, products])

  return (
    <div className="products-page container">
      <div className="products-page__header">
        <div>
          <p className="section-eyebrow">Curated Luxury</p>
          <h1 className="products-page__title">The Collection</h1>
        </div>
        <p className="products-page__count">{loading ? '...' : filtered.length} pieces</p>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Toolbar */}
      <div className="products-page__toolbar">
        <div className="products-page__search">
          <Search size={16} className="products-page__search-icon" />
          <input
            className="input products-page__search-input"
            type="text"
            placeholder="Search products or brands…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            aria-label="Search products"
          />
          {search && (
            <button className="products-page__clear" onClick={() => setSearch('')} aria-label="Clear search">
              <X size={14} />
            </button>
          )}
        </div>

        <button className="btn btn-ghost btn-sm products-page__filter-toggle" onClick={() => setShowFilters(!showFilters)}>
          <SlidersHorizontal size={15} /> Filters
        </button>

        <select className="input products-page__sort" value={sortBy} onChange={e => setSortBy(e.target.value)} aria-label="Sort products">
          <option value="default">Sort: Featured</option>
          <option value="price-asc">Price: Low → High</option>
          <option value="price-desc">Price: High → Low</option>
          <option value="name">Name A–Z</option>
        </select>
      </div>

      {/* Category filters */}
      {showFilters && (
        <div className="products-page__filters animate-fadeIn">
          <button
            className={`products-page__cat-btn ${selectedCat === 0 ? 'active' : ''}`}
            onClick={() => setSelectedCat(0)}
          >All</button>
          {categories.map(c => (
            <button
              key={c.id}
              className={`products-page__cat-btn ${selectedCat === c.id ? 'active' : ''}`}
              onClick={() => setSelectedCat(c.id)}
            >{c.category}</button>
          ))}
        </div>
      )}

      {/* Grid */}
      {filtered.length > 0 ? (
        <div className="grid-products">
          {filtered.map((p, i) => (
            <ProductCard key={p.p_id} product={p} style={{ animationDelay: `${i * 60}ms` }} />
          ))}
        </div>
      ) : (
        <div className="products-page__empty">
          <p>No pieces found matching your search.</p>
          <button className="btn btn-outline btn-sm mt-md" onClick={() => { setSearch(''); setSelectedCat(0); }}>
            Clear Filters
          </button>
        </div>
      )}
    </div>
  )
}
