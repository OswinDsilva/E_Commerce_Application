import React, { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ShoppingBag, ArrowLeft, Package } from 'lucide-react'
import { PRODUCTS } from '../data/mockData'
import { useCart } from '../context/CartContext'
import './ProductDetailPage.css'

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addToCart } = useCart()
  const [qty, setQty] = useState(1)
  const [added, setAdded] = useState(false)

  const product = PRODUCTS.find(p => p.p_id === parseInt(id))
  if (!product) return (
    <div className="container text-center section">
      <h2>Product not found</h2>
      <Link to="/products" className="btn btn-outline mt-lg">Back to Collection</Link>
    </div>
  )

  const inStock = product.stock > 0

  const handleAdd = () => {
    addToCart(product, qty)
    setAdded(true)
    setTimeout(() => setAdded(false), 2000)
  }

  const related = PRODUCTS.filter(p => p.category === product.category && p.p_id !== product.p_id).slice(0, 3)

  return (
    <div className="product-detail container">
      <Link to="/products" className="product-detail__back">
        <ArrowLeft size={16} /> Collection
      </Link>

      <div className="product-detail__grid">
        {/* Image */}
        <div className="product-detail__image-wrap">
          <img src={product.image} alt={product.product_name} className="product-detail__image" />
          <span className={`product-card__stock ${inStock ? 'product-card__stock--in' : 'product-card__stock--out'}`}>
            {inStock ? `In Stock (${product.stock} left)` : 'Out of Stock'}
          </span>
        </div>

        {/* Info */}
        <div className="product-detail__info animate-fadeUp">
          <p className="product-detail__brand">{product.brand}</p>
          <h1 className="product-detail__name">{product.product_name}</h1>
          <p className="product-detail__category badge badge-neutral">{product.category_name}</p>
          <p className="product-detail__price">${product.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
          <p className="product-detail__desc">{product.description}</p>

          <div className="product-detail__actions">
            <div className="qty-control">
              <button className="qty-control__btn" onClick={() => setQty(q => Math.max(1, q - 1))} aria-label="Decrease">−</button>
              <span className="qty-control__value">{qty}</span>
              <button className="qty-control__btn" onClick={() => setQty(q => Math.min(product.stock, q + 1))} disabled={!inStock} aria-label="Increase">+</button>
            </div>
            <button className="btn btn-primary btn-lg" onClick={handleAdd} disabled={!inStock} style={{flex:1}}>
              <ShoppingBag size={18} />
              {added ? 'Added to Cart!' : 'Add to Cart'}
            </button>
          </div>

          <div className="product-detail__meta">
            <div className="product-detail__meta-item">
              <Package size={15} />
              <span>Free insured shipping on all orders over $500</span>
            </div>
          </div>
        </div>
      </div>

      {/* Related */}
      {related.length > 0 && (
        <div className="product-detail__related">
          <h3>You May Also Like</h3>
          <div className="grid-products mt-lg">
            {related.map(p => (
              <Link key={p.p_id} to={`/products/${p.p_id}`} className="related-card card">
                <img src={p.image} alt={p.product_name} />
                <div style={{padding:'var(--space-md)'}}>
                  <p style={{fontSize:'0.7rem',color:'var(--color-cta)',fontWeight:700,letterSpacing:'0.1em',textTransform:'uppercase'}}>{p.brand}</p>
                  <p style={{fontFamily:'var(--font-heading)',fontSize:'1.1rem',color:'var(--color-primary)'}}>{p.product_name}</p>
                  <p style={{fontFamily:'var(--font-heading)',fontSize:'1.25rem',fontWeight:600,marginTop:'8px'}}>${p.price.toLocaleString()}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
