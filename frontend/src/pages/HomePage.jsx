import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, ChevronLeft, ChevronRight, Heart, Leaf, Search, ShoppingBag } from 'lucide-react'
import { PRODUCTS } from '../data/mockData'
import './HomePage.css'

const CATEGORY_SPOTLIGHTS = [
  {
    title: 'New Arrivals',
    cta: 'Explore Collection',
    image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=1200&q=80',
  },
  {
    title: 'Best Sellers',
    cta: 'Shop Favorites',
    image: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&q=80',
  },
  {
    title: 'Archive Sale',
    cta: 'Up to 40% Off',
    image: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1200&q=80',
  },
  {
    title: 'Gift Guide',
    cta: 'Curated Selection',
    image: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200&q=80',
  },
]

const PERSONALIZED = PRODUCTS.slice(0, 5)

export default function HomePage() {
  return (
    <div className="atelier-home">
      <section className="atelier-hero">
        <img
          className="atelier-hero__image"
          src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1800&q=80"
          alt="Elegant editorial fashion in a minimalist architectural setting"
        />
        <div className="atelier-hero__veil" aria-hidden="true" />
        <div className="container atelier-hero__content">
          <div className="atelier-hero__search">
            <Search size={16} />
            <input type="text" placeholder="Search the archive..." aria-label="Search the archive" />
          </div>

          <p className="atelier-hero__eyebrow">Limited Series</p>
          <h1 className="atelier-hero__title">The Summer Archive.</h1>
          <p className="atelier-hero__copy">
            A curated study of form, texture, and light. Explore our most ambitious collection to date.
          </p>

          <div className="atelier-hero__actions">
            <Link to="/products" className="atelier-btn atelier-btn--solid">
              Shop Now
            </Link>
            <Link to="/products" className="atelier-btn atelier-btn--link">
              View Lookbook
            </Link>
          </div>
        </div>

        <div className="atelier-hero__controls" aria-hidden="true">
          <button className="atelier-icon-btn">
            <ChevronLeft size={18} />
          </button>
          <button className="atelier-icon-btn">
            <ChevronRight size={18} />
          </button>
        </div>
      </section>

      <section className="container atelier-category-grid">
        {CATEGORY_SPOTLIGHTS.map((item) => (
          <article key={item.title} className="atelier-category-card">
            <h3>{item.title}</h3>
            <div className="atelier-category-card__media">
              <img src={item.image} alt={item.title} loading="lazy" />
            </div>
            <Link to="/products" className="atelier-inline-link">
              {item.cta}
            </Link>
          </article>
        ))}
      </section>

      <section className="atelier-rail-section">
        <div className="container">
          <div className="atelier-rail__header">
            <div>
              <p className="atelier-kicker">For You</p>
              <h2>Inspired by your history</h2>
            </div>
            <div className="atelier-rail__nav" aria-hidden="true">
              <button className="atelier-icon-btn atelier-icon-btn--soft">
                <ChevronLeft size={18} />
              </button>
              <button className="atelier-icon-btn atelier-icon-btn--soft">
                <ChevronRight size={18} />
              </button>
            </div>
          </div>

          <div className="atelier-rail" role="list" aria-label="Personalized products">
            {PERSONALIZED.map((product) => (
              <article key={product.p_id} className="atelier-rail-card" role="listitem">
                <div className="atelier-rail-card__media">
                  <img src={product.image} alt={product.product_name} loading="lazy" />
                  <button className="atelier-rail-card__fav" aria-label={`Save ${product.product_name}`}>
                    <Heart size={16} />
                  </button>
                </div>
                <div className="atelier-rail-card__meta">
                  <p>{product.category_name}</p>
                  <h4>{product.product_name}</h4>
                  <span>${product.price.toFixed(2)}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="container atelier-bento">
        <article className="atelier-bento__feature">
          <img
            src="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=1800&q=80"
            alt="Atmospheric fashion story in natural light"
            loading="lazy"
          />
          <div className="atelier-bento__feature-overlay">
            <p className="atelier-kicker atelier-kicker--light">Curated Series</p>
            <h2>The Summer Edit</h2>
            <Link to="/products" className="atelier-btn atelier-btn--soft">
              Discover Story
            </Link>
          </div>
        </article>

        <article className="atelier-bento__secondary">
          <img
            src="https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=1400&q=80"
            alt="Minimal and warm interior with refined materials"
            loading="lazy"
          />
          <div className="atelier-bento__secondary-overlay">
            <h3>Archive Essentials</h3>
            <p>Timeless pieces for the permanent wardrobe.</p>
            <Link to="/products" className="atelier-inline-link atelier-inline-link--light">
              Shop The Archive
            </Link>
          </div>
        </article>

        <article className="atelier-bento__text">
          <h3>Craftsmanship without compromise.</h3>
          <p>
            Every piece in our Atelier is born from a dialogue between artisan and material,
            ensuring a legacy that outlives the season.
          </p>
          <div className="atelier-bento__badge">
            <span>
              <Leaf size={18} />
            </span>
            Sustainable Sourcing
          </div>
        </article>
      </section>

      <div className="atelier-floating-cart" aria-hidden="true">
        <div className="atelier-floating-cart__thumbs">
          <img src={PRODUCTS[0].image} alt="" />
          <img src={PRODUCTS[1].image} alt="" />
        </div>
        <div className="atelier-floating-cart__divider" />
        <div className="atelier-floating-cart__cta">
          <span>Your Selection</span>
          <Link to="/cart" className="atelier-btn atelier-btn--mini">
            <ShoppingBag size={14} />
            Checkout
          </Link>
        </div>
      </div>

      <section className="atelier-journal">
        <div className="container atelier-journal__inner">
          <div>
            <p className="atelier-kicker">Journal</p>
            <h2>Receive early access and insight into our development.</h2>
          </div>
          <div className="atelier-journal__form">
            <input type="email" placeholder="Email Address" aria-label="Email address" />
            <button aria-label="Submit journal signup">
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}
