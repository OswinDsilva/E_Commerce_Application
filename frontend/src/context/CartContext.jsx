import React, { createContext, useContext, useState } from 'react'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [items, setItems] = useState([]) // { product, quantity }

  const addToCart = (product, quantity = 1) => {
    setItems(prev => {
      const existing = prev.find(i => i.product.p_id === product.p_id)
      if (existing) {
        return prev.map(i =>
          i.product.p_id === product.p_id
            ? { ...i, quantity: i.quantity + quantity }
            : i
        )
      }
      return [...prev, { product, quantity }]
    })
  }

  const removeFromCart = (productId) => {
    setItems(prev => prev.filter(i => i.product.p_id !== productId))
  }

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) { removeFromCart(productId); return }
    setItems(prev =>
      prev.map(i => i.product.p_id === productId ? { ...i, quantity } : i)
    )
  }

  const clearCart = () => setItems([])

  const cartCount = items.reduce((sum, i) => sum + i.quantity, 0)
  const cartTotal = items.reduce((sum, i) => sum + i.product.price * i.quantity, 0)

  return (
    <CartContext.Provider value={{ items, addToCart, removeFromCart, updateQuantity, clearCart, cartCount, cartTotal }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)
