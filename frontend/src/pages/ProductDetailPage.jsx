import React, { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ShoppingBag, ArrowLeft, Package } from 'lucide-react'
import { getProduct, listProducts, isBackendUnavailableError, getUserFacingErrorMessage } from '../services/api'
import { PRODUCTS } from '../data/mockData'
import { useCart } from '../context/CartContext'
import './ProductDetailPage.css'

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addToCart } = useCart()
  const [qty, setQty] = useState(1)
  const [added, setAdded] = useState(false)
  const [product, setProduct] = useState(null)
  const [related, setRelated] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true)
      setError(null)
      try {
        const productData = await getProduct(parseInt(id))
        setProduct(productData)
      } catch (err) {
        if (isBackendUnavailableError(err)) {
          // Fallback to mock data
          const mockProduct = PRODUCTS.find(p => p.p_id === parseInt(id))
          setProduct(mockProduct || null)
        } else {
          setError(getUserFacingErrorMessage(err, 'productDetail'))
        }
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id])

  useEffect(() => {
    const fetchRelated = async () => {
      if (!product) return
      try {
        const allProducts = await listProducts()
        const relatedProducts = allProducts
          .filter(p => p.category_id === product.category_id && p.p_id !== product.p_id)
          .slice(0, 3)
        setRelated(relatedProducts)
      } catch {
        // Fallback to mock data
        setRelated(PRODUCTS.filter(p => p.category === product.category && p.p_id !== product.p_id).slice(0, 3))
      }
    }

    fetchRelated()
  }, [product])
  if (loading) {
    return (
      <div className="container text-center section">
        <p>Loading product details...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container text-center section">
        <p className="text-error">{error}</p>
        <Link to="/products" className="btn btn-outline mt-lg">Back to Collection</Link>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="container text-center section">
        <h2>Product not found</h2>
        <Link to="/products" className="btn btn-outline mt-lg">Back to Collection</Link>
      </div>
    )
  }

  const inStock = product.quantity > 0

  const handleAdd = () => {
    addToCart(product, qty)
    setAdded(true)
    setTimeout(() => setAdded(false), 2000)
  }

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
            {inStock ? `In Stock (${product.quantity} left)` : 'Out of Stock'}
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
              <button className="qty-control__btn" onClick={() => setQty(q => Math.min(product.quantity, q + 1))} disabled={!inStock} aria-label="Increase">+</button>
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
