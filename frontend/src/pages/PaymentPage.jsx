import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CreditCard, CheckCircle, Plus, X } from 'lucide-react'
import { MOCK_BANK_ACCOUNTS } from '../data/mockData'
import { createBankAccount, getUserFacingErrorMessage, isBackendUnavailableError, listBankAccounts, payOrder } from '../services/api'
import { useAuth } from '../context/AuthContext'
import './PaymentPage.css'

export default function PaymentPage() {
  const { orderId } = useParams()
  const navigate = useNavigate()
  const { authMode } = useAuth()
  const [accounts, setAccounts] = useState(MOCK_BANK_ACCOUNTS)
  const [selectedAcc, setSelectedAcc] = useState(null)
  const [showAdd, setShowAdd] = useState(false)
  const [newAcc, setNewAcc] = useState({ acc_no: '', bank_name: '', expiry_date: '' })
  const [paid, setPaid] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    const loadAccounts = async () => {
      if (authMode !== 'backend') {
        return
      }

      try {
        const bankAccounts = await listBankAccounts()
        if (!active) return

        setAccounts(bankAccounts.length > 0 ? bankAccounts : MOCK_BANK_ACCOUNTS)
      } catch (loadError) {
        if (!active) return

        if (!isBackendUnavailableError(loadError)) {
          setError(getUserFacingErrorMessage(loadError, 'bankAccountsLoad'))
        }

        setAccounts(MOCK_BANK_ACCOUNTS)
      }
    }

    loadAccounts()

    return () => {
      active = false
    }
  }, [authMode])

  const handlePay = async () => {
    if (!selectedAcc) return
    setLoading(true)
    setError('')

    try {
      await payOrder(orderId, { acc_no: selectedAcc.acc_no })
      setPaid(true)
      setTimeout(() => navigate(`/invoice/${orderId}`), 2000)
    } catch (payError) {
      if (!isBackendUnavailableError(payError)) {
        setError(getUserFacingErrorMessage(payError, 'orderPayment'))
        setLoading(false)
        return
      }

      setPaid(true)
      setTimeout(() => navigate(`/invoice/${orderId}`), 2000)
    }

    setLoading(false)
  }

  const handleAddAccount = (e) => {
    e.preventDefault()
    if (!newAcc.acc_no || !newAcc.bank_name || !newAcc.expiry_date) return

    const payload = {
      ...newAcc,
      acc_no: parseInt(newAcc.acc_no, 10),
    }

    if (authMode !== 'backend') {
      setAccounts(a => [...a, payload])
      setShowAdd(false)
      setNewAcc({ acc_no: '', bank_name: '', expiry_date: '' })
      return
    }

    setError('')
    createBankAccount(payload)
      .then(account => {
        setAccounts(a => [...a, account])
        setShowAdd(false)
        setNewAcc({ acc_no: '', bank_name: '', expiry_date: '' })
      })
      .catch(addError => {
        if (isBackendUnavailableError(addError)) {
          setAccounts(a => [...a, payload])
          setShowAdd(false)
          setNewAcc({ acc_no: '', bank_name: '', expiry_date: '' })
          return
        }

        setError(getUserFacingErrorMessage(addError, 'bankAccountsCreate'))
      })
  }

  if (paid) return (
    <div className="payment-page container text-center">
      <div className="payment-success animate-fadeUp">
        <CheckCircle size={72} className="payment-success__icon" />
        <h2>Payment Successful</h2>
        <p>Order #{orderId} has been confirmed. Redirecting to your invoice…</p>
      </div>
    </div>
  )

  return (
    <div className="payment-page container">
      <h1>Complete Payment</h1>
      <p className="payment-page__sub">Order #{orderId} · Select a bank account to pay</p>
      {error && <div className="auth-error" style={{ marginBottom: 'var(--space-md)' }}>{error}</div>}

      <div className="payment-layout">
        <div>
          <h3 className="payment-section-title">Your Bank Accounts</h3>
          <div className="payment-accounts">
            {accounts.map(acc => (
              <div
                key={acc.acc_no}
                className={`payment-account card ${selectedAcc?.acc_no === acc.acc_no ? 'payment-account--selected' : ''}`}
                onClick={() => setSelectedAcc(acc)}
                role="button"
                tabIndex={0}
                onKeyDown={e => e.key === 'Enter' && setSelectedAcc(acc)}
                aria-label={`Select ${acc.bank_name}`}
              >
                <div className="payment-account__icon"><CreditCard size={22} /></div>
                <div className="payment-account__info">
                  <p className="payment-account__bank">{acc.bank_name}</p>
                  <p className="payment-account__meta">Acc #{acc.acc_no} · Expires {acc.expiry_date}</p>
                </div>
                {selectedAcc?.acc_no === acc.acc_no && (
                  <CheckCircle size={20} className="payment-account__check" />
                )}
              </div>
            ))}
          </div>

          <button className="btn btn-ghost btn-sm payment-add-btn" onClick={() => setShowAdd(s => !s)}>
            {showAdd ? <X size={15} /> : <Plus size={15} />}
            {showAdd ? 'Cancel' : 'Add Bank Account'}
          </button>

          {showAdd && (
            <form onSubmit={handleAddAccount} className="payment-add-form glass-card animate-fadeIn">
              <h4>Add New Account</h4>
              <div className="input-group">
                <label className="input-label" htmlFor="pay-accno">Account Number</label>
                <input id="pay-accno" className="input" type="number" placeholder="123456789" value={newAcc.acc_no} onChange={e => setNewAcc(a => ({...a, acc_no: e.target.value}))} />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="pay-bank">Bank Name</label>
                <input id="pay-bank" className="input" type="text" placeholder="e.g. Creston Private Bank" value={newAcc.bank_name} onChange={e => setNewAcc(a => ({...a, bank_name: e.target.value}))} />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="pay-expiry">Expiry Date</label>
                <input id="pay-expiry" className="input" type="date" value={newAcc.expiry_date} onChange={e => setNewAcc(a => ({...a, expiry_date: e.target.value}))} />
              </div>
              <button type="submit" className="btn btn-primary btn-sm">Save Account</button>
            </form>
          )}
        </div>

        <div className="payment-panel glass-card">
          <h3>Payment Details</h3>
          {selectedAcc ? (
            <>
              <p className="payment-panel__selected">Paying with:<br /><strong>{selectedAcc.bank_name}</strong></p>
              <button className="btn btn-gold btn-lg payment-pay-btn" onClick={handlePay} disabled={loading}>
                {loading ? 'Processing…' : 'Confirm Payment'}
              </button>
            </>
          ) : (
            <p className="payment-panel__hint">Select a bank account to continue.</p>
          )}
        </div>
      </div>
    </div>
  )
}
