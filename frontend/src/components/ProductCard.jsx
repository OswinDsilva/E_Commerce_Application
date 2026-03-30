import React from 'react'
import { Link } from 'react-router-dom'
import { ShoppingBag, Eye } from 'lucide-react'
import { useCart } from '../context/CartContext'
import './ProductCard.css'

export default function ProductCard({ product, style }) {
  const { addToCart } = useCart()
  const inStock = product.stock > 0

  return (
    <article className="product-card card animate-fadeUp" style={style}>
      <div className="product-card__image-wrap">
        <img
          src={product.image}
          alt={product.product_name}
          className="product-card__image"
          loading="lazy"
        />
        <div className="product-card__overlay">
          <Link to={`/products/${product.p_id}`} className="product-card__overlay-btn" aria-label="View product">
            <Eye size={18} />
          </Link>
        </div>
        <span className={`product-card__stock ${inStock ? 'product-card__stock--in' : 'product-card__stock--out'}`}>
          {inStock ? 'In Stock' : 'Out of Stock'}
        </span>
      </div>

      <div className="product-card__body">
        <p className="product-card__brand">{product.brand}</p>
        <h3 className="product-card__name">
          <Link to={`/products/${product.p_id}`}>{product.product_name}</Link>
        </h3>
        <p className="product-card__category">{product.category_name}</p>
        <div className="product-card__footer">
          <span className="product-card__price">${product.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => addToCart(product)}
            disabled={!inStock}
            aria-label={`Add ${product.product_name} to cart`}
          >
            <ShoppingBag size={15} />
            Add
          </button>
        </div>
      </div>
    </article>
  )
}
