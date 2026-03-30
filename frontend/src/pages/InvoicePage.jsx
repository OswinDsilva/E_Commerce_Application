import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { FileText, Download, ArrowLeft } from 'lucide-react'
import { MOCK_ORDERS } from '../data/mockData'
import './InvoicePage.css'

export default function InvoicePage() {
  const { orderId } = useParams()
  const order = MOCK_ORDERS.find(o => o.o_id === parseInt(orderId)) || {
    o_id: parseInt(orderId),
    order_date: new Date().toISOString().split('T')[0],
    status: 'PAID',
    total_amount: 0,
    items: [],
  }

  const invoiceDate = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })

  return (
    <div className="invoice-page container">
      <div className="invoice-page__actions">
        <Link to="/orders" className="btn btn-ghost btn-sm"><ArrowLeft size={15} /> Back to Orders</Link>
        <button className="btn btn-outline btn-sm" onClick={() => window.print()} aria-label="Download invoice">
          <Download size={15} /> Download PDF
        </button>
      </div>

      <div className="invoice card">
        {/* Header */}
        <div className="invoice__head">
          <div>
            <div className="invoice__brand">
              <span className="invoice__brand-the">The</span>
              <span className="invoice__brand-name">Atelier</span>
            </div>
            <p className="invoice__sub">Curated Luxury Since 2010</p>
          </div>
          <div className="invoice__meta">
            <div className="invoice__meta-row">
              <span>Invoice</span>
              <span>#{order.o_id}</span>
            </div>
            <div className="invoice__meta-row">
              <span>Order Date</span>
              <span>{new Date(order.order_date).toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' })}</span>
            </div>
            <div className="invoice__meta-row">
              <span>Invoice Date</span>
              <span>{invoiceDate}</span>
            </div>
            <div className="invoice__meta-row">
              <span>Status</span>
              <span className="badge badge-success">{order.status}</span>
            </div>
          </div>
        </div>

        <hr className="divider" />

        {/* Addresses */}
        <div className="invoice__addresses">
          <div>
            <h4 className="invoice__addr-label">Shipping Address</h4>
            <address className="invoice__addr">123 Maison Noir Avenue<br />Bandra West, Mumbai 400 050<br />Maharashtra, India</address>
          </div>
          <div>
            <h4 className="invoice__addr-label">Billing Address</h4>
            <address className="invoice__addr">123 Maison Noir Avenue<br />Bandra West, Mumbai 400 050<br />Maharashtra, India</address>
          </div>
        </div>

        <hr className="divider" />

        {/* Items table */}
        <table className="invoice__table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {order.items.map(item => (
              <tr key={item.p_id}>
                <td>{item.product_name}</td>
                <td>{item.quantity}</td>
                <td>${item.price_at_purchase.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                <td>${(item.price_at_purchase * item.quantity).toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="invoice__table-total">
              <td colSpan={3}>Total</td>
              <td>${order.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
            </tr>
          </tfoot>
        </table>

        <div className="invoice__footer">
          <p>Thank you for your purchase at The Atelier.</p>
          <p className="invoice__footer-sub">For any queries, contact us at support@theatelier.com</p>
        </div>
      </div>
    </div>
  )
}
