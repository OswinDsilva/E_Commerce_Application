import React from 'react'
import { Link } from 'react-router-dom'
import { Instagram, Twitter, Facebook } from 'lucide-react'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div className="footer__brand">
          <div className="footer__logo">
            <span className="footer__logo-the">The</span>
            <span className="footer__logo-name">Atelier</span>
          </div>
          <p className="footer__tagline">Curated luxury, delivered with intention.</p>
          <div className="footer__socials">
            <a href="#" aria-label="Instagram" className="footer__social-link"><Instagram size={18} /></a>
            <a href="#" aria-label="Twitter" className="footer__social-link"><Twitter size={18} /></a>
            <a href="#" aria-label="Facebook" className="footer__social-link"><Facebook size={18} /></a>
          </div>
        </div>

        <div className="footer__col">
          <h4 className="footer__col-title">Shop</h4>
          <ul>
            <li><Link to="/products">All Collections</Link></li>
            <li><Link to="/products?category=clothing">Clothing</Link></li>
            <li><Link to="/products?category=accessories">Accessories</Link></li>
            <li><Link to="/products?category=footwear">Footwear</Link></li>
          </ul>
        </div>

        <div className="footer__col">
          <h4 className="footer__col-title">Account</h4>
          <ul>
            <li><Link to="/login">Sign In</Link></li>
            <li><Link to="/register">Create Account</Link></li>
            <li><Link to="/orders">My Orders</Link></li>
            <li><Link to="/cart">My Cart</Link></li>
          </ul>
        </div>

        <div className="footer__col">
          <h4 className="footer__col-title">Company</h4>
          <ul>
            <li><a href="#">About Us</a></li>
            <li><a href="#">Privacy Policy</a></li>
            <li><a href="#">Terms of Service</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
        </div>
      </div>

      <div className="footer__bottom">
        <div className="container">
          <p>&copy; 2026 The Atelier. All rights reserved.</p>
          <p className="footer__bottom-right">Luxury crafted with care.</p>
        </div>
      </div>
    </footer>
  )
}
