import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Package, FileText, ChevronRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getOrder, getUserFacingErrorMessage, isBackendUnavailableError, listOrders } from '../services/api'
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
  const { authMode } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    const loadOrders = async () => {
      setLoading(true)
      setError('')

      if (authMode !== 'backend') {
        if (!active) return
        setOrders(MOCK_ORDERS)
        setLoading(false)
        return
      }

      try {
        const backendOrders = await listOrders()
        if (!active) return

        const detailedOrders = await Promise.all(
          backendOrders.map(async order => {
            try {
              const detail = await getOrder(order.o_id)
              return { ...order, items: detail.items }
            } catch {
              return { ...order, items: [] }
            }
          })
        )

        if (!active) return
        setOrders(detailedOrders)
      } catch (loadError) {
        if (!active) return

        if (isBackendUnavailableError(loadError)) {
          setOrders(MOCK_ORDERS)
        } else {
          setOrders([])
          setError(getUserFacingErrorMessage(loadError, 'ordersLoad'))
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadOrders()

    return () => {
      active = false
    }
  }, [authMode])

  if (loading) {
    return (
      <div className="container text-center section">
        <Package size={56} style={{ color: 'var(--color-border)', margin: '0 auto 24px' }} />
        <h2>Loading Orders</h2>
        <p>Fetching your recent purchases…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container text-center section">
        <Package size={56} style={{ color: 'var(--color-border)', margin: '0 auto 24px' }} />
        <h2>Orders Unavailable</h2>
        <p>{error}</p>
      </div>
    )
  }

  if (orders.length === 0) return (
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
        {orders.map(order => (
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
                {(order.items || []).length > 0 ? order.items.map(item => (
                  <p key={item.p_id} className="order-card__item-row">
                    {item.product_name} <span>× {item.quantity}</span>
                  </p>
                )) : (
                  <p className="order-card__item-row">Item details unavailable</p>
                )}
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
