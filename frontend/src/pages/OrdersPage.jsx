import React from 'react'
import { Link } from 'react-router-dom'
import { Package, FileText, ChevronRight } from 'lucide-react'
import { MOCK_ORDERS } from '../data/mockData'
import './OrdersPage.css'

const STATUS_BADGE = {
  CREATED: 'badge-neutral',
  PAID:    'badge-success',
  SHIPPED: 'badge-gold',
  DELIVERED: 'badge-dark',
  CANCELLED: 'badge-error',
}

export default function OrdersPage() {
  if (MOCK_ORDERS.length === 0) return (
    <div className="container text-center section">
      <Package size={56} style={{color:'var(--color-border)',margin:'0 auto 24px'}} />
      <h2>No Orders Yet</h2>
      <p>When you place an order it will appear here.</p>
      <Link to="/products" className="btn btn-primary mt-lg">Browse Collection</Link>
    </div>
  )

  return (
    <div className="orders-page container">
      <div className="orders-page__header">
        <p className="section-eyebrow">Your Account</p>
        <h1>Orders</h1>
      </div>

      <div className="orders-list">
        {MOCK_ORDERS.map(order => (
          <div key={order.o_id} className="order-card card">
            <div className="order-card__header">
              <div className="order-card__id">
                <Package size={16} />
                <span>Order #{order.o_id}</span>
              </div>
              <span className={`badge ${STATUS_BADGE[order.status] || 'badge-neutral'}`}>{order.status}</span>
            </div>
            <div className="order-card__body">
              <div className="order-card__items">
                {order.items.map(item => (
                  <p key={item.p_id} className="order-card__item-row">
                    {item.product_name} <span>× {item.quantity}</span>
                  </p>
                ))}
              </div>
              <div className="order-card__meta">
                <p className="order-card__date">Placed: {new Date(order.order_date).toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' })}</p>
                <p className="order-card__total">${order.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
              </div>
            </div>
            <div className="order-card__footer">
              {order.status === 'CREATED' && (
                <Link to={`/payment/${order.o_id}`} className="btn btn-gold btn-sm">
                  Complete Payment
                </Link>
              )}
              {order.status === 'PAID' && (
                <Link to={`/invoice/${order.o_id}`} className="btn btn-outline btn-sm">
                  <FileText size={14} /> View Invoice
                </Link>
              )}
              <Link to={`/orders`} className="order-card__detail-link">
                Details <ChevronRight size={14} />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
