import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import './AuthPage.css'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.username || !form.password) { setError('Please fill in all fields.'); return }
    setLoading(true)
    // TODO: POST /api/auth/login
    await new Promise(r => setTimeout(r, 800))
    // Mock: treat any login as valid; role depends on username
    const mockUser = {
      u_id: 1,
      username: form.username,
      email: `${form.username}@example.com`,
      role: form.username.toLowerCase() === 'admin' ? 'ADMIN' : 'USER',
    }
    login(mockUser)
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
        <h2 className="auth-card__title">Welcome Back</h2>
        <p className="auth-card__sub">Sign in to continue your curated experience.</p>

        <form onSubmit={handleSubmit} noValidate className="auth-form">
          {error && <div className="auth-error">{error}</div>}
          <div className="input-group">
            <label className="input-label" htmlFor="login-username">Username</label>
            <input
              id="login-username"
              className="input"
              type="text"
              value={form.username}
              onChange={e => setForm(f => ({...f, username: e.target.value}))}
              placeholder="your_username"
              autoComplete="username"
            />
          </div>
          <div className="input-group">
            <label className="input-label" htmlFor="login-password">Password</label>
            <div className="auth-pw-wrap">
              <input
                id="login-password"
                className="input"
                type={showPw ? 'text' : 'password'}
                value={form.password}
                onChange={e => setForm(f => ({...f, password: e.target.value}))}
                placeholder="••••••••"
                autoComplete="current-password"
              />
              <button type="button" className="auth-pw-toggle" onClick={() => setShowPw(s => !s)} aria-label="Toggle password">
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-lg auth-submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p className="auth-card__footer">
          Don't have an account? <Link to="/register">Create one</Link>
        </p>
        <p className="auth-card__hint">Tip: use username <strong>admin</strong> to access Admin Dashboard.</p>
      </div>
    </div>
  )
}
