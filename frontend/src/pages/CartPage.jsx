import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Trash2, ShoppingBag, ArrowRight } from 'lucide-react'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import './CartPage.css'

export default function CartPage() {
  const { items, removeFromCart, updateQuantity, cartTotal, clearCart } = useCart()
  const { user } = useAuth()
  const navigate = useNavigate()

  if (items.length === 0) return (
    <div className="cart-empty container text-center">
      <div className="cart-empty__icon"><ShoppingBag size={56} /></div>
      <h2>Your Cart is Empty</h2>
      <p>Discover our curated collection and add your first piece.</p>
      <Link to="/products" className="btn btn-primary mt-lg">Browse Collection</Link>
    </div>
  )

  const handleCheckout = () => {
    if (!user) { navigate('/login'); return }
    navigate('/checkout')
  }

  return (
    <div className="cart-page container">
      <div className="cart-page__header">
        <h1>Your Cart</h1>
        <button className="btn btn-ghost btn-sm" onClick={clearCart}>Clear All</button>
      </div>

      <div className="cart-page__layout">
        {/* Items */}
        <div className="cart-items">
          {items.map(({ product, quantity }) => (
            <div key={product.p_id} className="cart-item card">
              <img src={product.image} alt={product.product_name} className="cart-item__image" />
              <div className="cart-item__info">
                <p className="cart-item__brand">{product.brand}</p>
                <h3 className="cart-item__name">{product.product_name}</h3>
                <p className="cart-item__category">{product.category_name}</p>
              </div>
              <div className="cart-item__controls">
                <div className="qty-control">
                  <button className="qty-control__btn" onClick={() => updateQuantity(product.p_id, quantity - 1)}>−</button>
                  <span className="qty-control__value">{quantity}</span>
                  <button className="qty-control__btn" onClick={() => updateQuantity(product.p_id, quantity + 1)}>+</button>
                </div>
                <p className="cart-item__price">${(product.price * quantity).toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
                <button className="cart-item__remove" onClick={() => removeFromCart(product.p_id)} aria-label="Remove item">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="cart-summary glass-card">
          <h3 className="cart-summary__title">Order Summary</h3>
          <div className="cart-summary__rows">
            {items.map(({ product, quantity }) => (
              <div className="cart-summary__row" key={product.p_id}>
                <span>{product.product_name} × {quantity}</span>
                <span>${(product.price * quantity).toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
              </div>
            ))}
          </div>
          <div className="cart-summary__divider" />
          <div className="cart-summary__total">
            <span>Total</span>
            <span className="cart-summary__total-amount">${cartTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          </div>
          <button className="btn btn-primary btn-lg cart-summary__cta" onClick={handleCheckout}>
            Proceed to Checkout <ArrowRight size={18} />
          </button>
          <Link to="/products" className="btn btn-ghost btn-sm cart-summary__continue">← Continue Shopping</Link>
        </div>
      </div>
    </div>
  )
}
