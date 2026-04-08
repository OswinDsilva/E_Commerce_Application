import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, MapPin, ShieldCheck, Truck, X } from 'lucide-react'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { createOrder, getUserFacingErrorMessage, isBackendUnavailableError } from '../services/api'
import './CheckoutPage.css'

export default function CheckoutPage() {
  const { items, cartTotal, clearCart, removeFromCart } = useCart()
  const { authMode } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ shipping: '', billing: '', sameAddress: true })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const shippingFee = 0
  const grandTotal = cartTotal + shippingFee

  const set = (k) => (e) => setForm(f => ({...f, [k]: e.target.value}))

  const handleSubmit = async (e) => {
    e.preventDefault()
    const shippingAddress = form.shipping.trim()
    const billingAddress = form.sameAddress ? shippingAddress : form.billing.trim()

    if (!shippingAddress || (!form.sameAddress && !billingAddress)) return

    setLoading(true)
    setError('')

    const payload = {
      items: items.map(({ product, quantity }) => ({ p_id: product.p_id, quantity })),
      shipping_address: shippingAddress,
      billing_address: billingAddress,
    }

    if (authMode === 'backend') {
      try {
        const order = await createOrder(payload)
        clearCart()
        setLoading(false)
        navigate(`/payment/${order.o_id}`)
        return
      } catch (submitError) {
        if (!isBackendUnavailableError(submitError)) {
          setError(getUserFacingErrorMessage(submitError, 'orderCreate'))
          setLoading(false)
          return
        }
      }
    }

    const mockOrderId = Math.floor(Math.random() * 9000) + 1000
    clearCart()
    setLoading(false)
    navigate(`/payment/${mockOrderId}`)
  }

  if (items.length === 0) {
    return (
      <div className="checkout-page container">
        <div className="checkout-empty">
          <p className="checkout-eyebrow">Checkout</p>
          <h1>Your selection is empty.</h1>
          <p>Add a few pieces to your cart and return to complete your order.</p>
          <Link to="/products" className="btn btn-primary btn-lg">
            Explore Collection <ArrowRight size={18} />
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="checkout-page container">
      <header className="checkout-header animate-fadeUp">
        <p className="checkout-eyebrow">Secure Checkout</p>
        <h1 className="checkout-page__title">Finalise Your Atelier Order</h1>
        <p className="checkout-page__subtitle">
          Review your delivery details and confirm payment. Every order is insured and packed with white-glove care.
        </p>
        {error && <div className="auth-error" style={{ marginTop: 'var(--space-md)' }}>{error}</div>}
      </header>

      <div className="checkout-layout">
        <form onSubmit={handleSubmit} className="checkout-form" noValidate>
          <div className="checkout-section checkout-editorial-card">
            <div className="checkout-section__icon"><MapPin size={16} /></div>
            <div className="checkout-section__body">
              <h3>Shipping Address</h3>
              <p className="checkout-section__hint">Include apartment, city, state, and postal code for accurate delivery.</p>
              <textarea
                className="input checkout-textarea"
                rows={3}
                placeholder="Full address including street, city, state, PIN..."
                value={form.shipping}
                onChange={set('shipping')}
                required
                aria-label="Shipping address"
              />
              <label className="checkout-same-label">
                <input type="checkbox" checked={form.sameAddress} onChange={e => setForm(f => ({...f, sameAddress: e.target.checked}))} />
                <span>Billing address same as shipping</span>
              </label>
              {!form.sameAddress && (
                <textarea
                  className="input checkout-textarea mt-sm"
                  rows={3}
                  placeholder="Billing address..."
                  value={form.billing}
                  onChange={set('billing')}
                  aria-label="Billing address"
                />
              )}
            </div>
          </div>

          <div className="checkout-section checkout-editorial-card">
            <div className="checkout-section__icon"><Truck size={16} /></div>
            <div className="checkout-section__body">
              <h3>Delivery Method</h3>
              <p className="checkout-delivery-row">
                <span>White-Glove Standard (3-5 business days)</span>
                <strong>Complimentary</strong>
              </p>
              <p className="checkout-delivery-note">Tracked, insured, and signature-protected for every parcel.</p>
            </div>
          </div>

          <div className="checkout-assurance">
            <ShieldCheck size={16} />
            <span>All transactions are encrypted and protected.</span>
          </div>

          <div className="checkout-actions">
            <button type="submit" className="btn btn-primary btn-lg checkout-submit" disabled={loading}>
              {loading ? 'Placing Order…' : 'Place Order & Proceed to Payment'} <ArrowRight size={18} />
            </button>
            <button type="button" className="btn btn-outline btn-lg" onClick={() => navigate('/cart')}>
              Back to Cart
            </button>
          </div>
        </form>

        <aside className="checkout-summary">
          <h3>Order Summary</h3>
          <div className="checkout-summary__items">
            {items.map(({ product, quantity }) => (
              <div className="checkout-summary__row" key={product.p_id}>
                <div className="checkout-summary__item-info">
                  <img src={product.image} alt={product.product_name} loading="lazy" />
                  <div>
                    <p>{product.product_name}</p>
                    <span>{product.brand} · Qty {quantity}</span>
                  </div>
                </div>
                <div className="checkout-summary__item-actions">
                  <strong>${(product.price * quantity).toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong>
                  <button
                    type="button"
                    className="checkout-remove-btn"
                    onClick={() => removeFromCart(product.p_id)}
                    aria-label={`Remove ${product.product_name} from cart`}
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="checkout-summary__line">
            <span>Subtotal</span>
            <span>${cartTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          </div>
          <div className="checkout-summary__line">
            <span>Delivery</span>
            <span>{shippingFee === 0 ? 'Complimentary' : `$${shippingFee.toFixed(2)}`}</span>
          </div>

          <div className="checkout-summary__total">
            <span>Total</span>
            <span>${grandTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          </div>

          <p className="checkout-summary__footnote">By continuing, you agree to our terms and atelier shipping policy.</p>
        </aside>
      </div>
    </div>
  )
}
