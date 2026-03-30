import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import './AuthPage.css'

export default function RegisterPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', phone: '', password: '', confirm: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (key) => (e) => setForm(f => ({...f, [key]: e.target.value}))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.username || !form.email || !form.phone || !form.password) { setError('Please fill in all fields.'); return }
    if (form.password !== form.confirm) { setError('Passwords do not match.'); return }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setLoading(true)
    // TODO: POST /api/auth/register
    await new Promise(r => setTimeout(r, 900))
    const newUser = { u_id: Date.now(), username: form.username, email: form.email, role: 'USER' }
    login(newUser)
    setLoading(false)
    navigate('/')
  }

  return (
    <div className="auth-page">
      <div className="auth-card glass-card animate-fadeUp">
        <div className="auth-card__brand">
          <span className="auth-brand-the">The</span>
          <span className="auth-brand-name">Atelier</span>
        </div>
        <h2 className="auth-card__title">Create Account</h2>
        <p className="auth-card__sub">Join The Atelier and begin your curated journey.</p>

        <form onSubmit={handleSubmit} noValidate className="auth-form">
          {error && <div className="auth-error">{error}</div>}
          <div className="input-group">
            <label className="input-label" htmlFor="reg-username">Username</label>
            <input id="reg-username" className="input" type="text" value={form.username} onChange={set('username')} placeholder="your_username" autoComplete="username" />
          </div>
          <div className="input-group">
            <label className="input-label" htmlFor="reg-email">Email</label>
            <input id="reg-email" className="input" type="email" value={form.email} onChange={set('email')} placeholder="you@example.com" autoComplete="email" />
          </div>
          <div className="input-group">
            <label className="input-label" htmlFor="reg-phone">Phone</label>
            <input id="reg-phone" className="input" type="tel" value={form.phone} onChange={set('phone')} placeholder="+91 98765 43210" autoComplete="tel" />
          </div>
          <div className="input-group">
            <label className="input-label" htmlFor="reg-password">Password</label>
            <div className="auth-pw-wrap">
              <input id="reg-password" className="input" type={showPw ? 'text' : 'password'} value={form.password} onChange={set('password')} placeholder="Min 6 characters" autoComplete="new-password" />
              <button type="button" className="auth-pw-toggle" onClick={() => setShowPw(s => !s)} aria-label="Toggle password"><Eye size={16} /></button>
            </div>
          </div>
          <div className="input-group">
            <label className="input-label" htmlFor="reg-confirm">Confirm Password</label>
            <input id="reg-confirm" className="input" type="password" value={form.confirm} onChange={set('confirm')} placeholder="Repeat password" autoComplete="new-password" />
          </div>
          <button type="submit" className="btn btn-primary btn-lg auth-submit" disabled={loading}>
            {loading ? 'Creating Account…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-card__footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
