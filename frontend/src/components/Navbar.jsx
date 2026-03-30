import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { ShoppingBag, User, Menu, X, LayoutDashboard, LogOut, Package } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import './Navbar.css'

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const { cartCount } = useCart()
  const navigate = useNavigate()
  const location = useLocation()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    setMenuOpen(false)
    setUserMenuOpen(false)
  }, [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
      <div className="container navbar__inner">
        {/* Logo */}
        <Link to="/" className="navbar__logo">
          <span className="navbar__logo-the">The</span>
          <span className="navbar__logo-name">Atelier</span>
        </Link>

        {/* Desktop Nav */}
        <ul className="navbar__links">
          <li><Link to="/products" className={location.pathname === '/products' ? 'active' : ''}>Collection</Link></li>
          {user && <li><Link to="/orders" className={location.pathname === '/orders' ? 'active' : ''}>Orders</Link></li>}
          {isAdmin && <li><Link to="/admin" className={location.pathname === '/admin' ? 'active' : ''}>Dashboard</Link></li>}
        </ul>

        {/* Actions */}
        <div className="navbar__actions">
          <Link to="/cart" className="navbar__icon-btn" aria-label="Shopping cart">
            <ShoppingBag size={20} />
            {cartCount > 0 && <span className="navbar__cart-badge">{cartCount}</span>}
          </Link>

          {user ? (
            <div className="navbar__user-menu">
              <button
                className="navbar__icon-btn navbar__user-btn"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                aria-label="User menu"
              >
                <User size={20} />
                <span className="navbar__username">{user.username}</span>
              </button>
              {userMenuOpen && (
                <div className="navbar__dropdown animate-fadeIn">
                  <Link to="/orders" className="navbar__dropdown-item">
                    <Package size={15} /> My Orders
                  </Link>
                  {isAdmin && (
                    <Link to="/admin" className="navbar__dropdown-item">
                      <LayoutDashboard size={15} /> Admin Dashboard
                    </Link>
                  )}
                  <hr className="navbar__dropdown-divider" />
                  <button className="navbar__dropdown-item navbar__dropdown-item--danger" onClick={handleLogout}>
                    <LogOut size={15} /> Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="btn btn-primary btn-sm">Sign In</Link>
          )}

          <button className="navbar__mobile-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="navbar__mobile-menu animate-fadeIn">
          <Link to="/products">Collection</Link>
          {user && <Link to="/orders">My Orders</Link>}
          {isAdmin && <Link to="/admin">Admin Dashboard</Link>}
          {!user && <Link to="/login" className="btn btn-primary btn-sm" style={{width:'fit-content'}}>Sign In</Link>}
          {user && <button onClick={handleLogout} className="btn btn-ghost btn-sm" style={{width:'fit-content'}}>Sign Out</button>}
        </div>
      )}
    </nav>
  )
}
