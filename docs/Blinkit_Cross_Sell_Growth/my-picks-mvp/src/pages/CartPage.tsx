import React, { useState } from 'react'
import { ShoppingBag, Trash2, ChevronRight, CheckCircle } from 'lucide-react'
import { PRODUCTS } from '../data/products'
import { useAppStore } from '../state/StoreContext'
import { INTENT_META } from '../types'

interface Props {
  onBack: () => void
  onContinueShopping: () => void
}

export default function CartPage({ onBack, onContinueShopping }: Props) {
  const { cart, removeFromCart, placeOrder } = useAppStore()
  const [orderPlaced, setOrderPlaced] = useState(false)

  const activeItems = cart.filter(i => !i.purchasedAt)
  const total = activeItems.reduce((sum, item) => {
    const product = PRODUCTS.find(p => p.id === item.productId)
    return sum + (product?.price ?? 0)
  }, 0)

  const handlePlaceOrder = () => {
    placeOrder()
    setOrderPlaced(true)
  }

  if (orderPlaced) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen px-6 text-center pb-20 bg-white">
        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mb-5">
          <CheckCircle size={40} className="text-green-500" />
        </div>
        <h1 className="text-2xl font-black text-gray-900">🎉 Order Placed!</h1>
        <p className="text-sm text-gray-500 mt-2 max-w-xs">Your My Pick became a purchase. Thanks for shopping!</p>
        <div className="mt-3 bg-pink-50 rounded-xl px-4 py-2 text-sm text-pink-700 font-medium border border-pink-100">
          Wishlist → Purchase conversion recorded ✓
        </div>
        <button
          onClick={onContinueShopping}
          className="mt-8 px-8 py-3 rounded-full bg-pink-600 text-white font-bold text-sm shadow hover:bg-pink-700 transition-colors"
        >
          Continue Shopping
        </button>
      </div>
    )
  }

  if (activeItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen px-8 text-center pb-20 bg-white">
        <ShoppingBag size={52} className="text-gray-200 mb-4" />
        <h2 className="text-lg font-bold text-gray-700">Your Bag is Empty</h2>
        <p className="text-sm text-gray-400 mt-2">Add items to your bag to start shopping.</p>
        <button
          onClick={onContinueShopping}
          className="mt-6 px-6 py-2.5 bg-pink-600 text-white rounded-full font-bold text-sm"
        >
          Start Shopping
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col pb-36 min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white px-4 py-4 sticky top-0 z-30 shadow-sm">
        <h1 className="text-lg font-black text-gray-900">Your Bag</h1>
        <p className="text-xs text-gray-500">{activeItems.length} item{activeItems.length > 1 ? 's' : ''}</p>
      </div>

      {/* Items */}
      <div className="mt-3 space-y-3 px-4">
        {activeItems.map(cartItem => {
          const product = PRODUCTS.find(p => p.id === cartItem.productId)
          if (!product) return null

          return (
            <div key={cartItem.productId} className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-50 flex gap-3 p-3">
              <img
                src={product.image}
                alt={product.name}
                className="w-20 h-24 object-cover rounded-xl bg-gray-100 flex-shrink-0"
                onError={(e) => {
                  ;(e.target as HTMLImageElement).src = `https://via.placeholder.com/80x96/f3f4f6/9ca3af?text=${encodeURIComponent(product.brand[0])}`
                }}
              />
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <p className="text-[10px] text-gray-500 font-semibold uppercase">{product.brand}</p>
                  <p className="text-sm font-medium text-gray-800 leading-tight mt-0.5">{product.name}</p>
                  <p className="text-xs text-gray-500 mt-1">Size: {cartItem.size}</p>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="text-base font-black text-gray-900">₹{product.price.toLocaleString()}</span>
                    <span className="text-xs text-gray-400 line-through">₹{product.originalPrice.toLocaleString()}</span>
                  </div>
                  <button
                    onClick={() => removeFromCart(cartItem.productId)}
                    className="w-7 h-7 rounded-full hover:bg-red-50 flex items-center justify-center transition-colors"
                  >
                    <Trash2 size={14} className="text-gray-400 hover:text-red-500" />
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Price Summary */}
      <div className="mx-4 mt-3 bg-white rounded-2xl p-4 shadow-sm border border-gray-50">
        <h3 className="text-sm font-bold text-gray-800 mb-3">Price Details</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between text-gray-600">
            <span>Total MRP</span>
            <span>₹{activeItems.reduce((s, i) => s + (PRODUCTS.find(p => p.id === i.productId)?.originalPrice ?? 0), 0).toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-green-600 font-medium">
            <span>Discount on MRP</span>
            <span>-₹{(activeItems.reduce((s, i) => s + (PRODUCTS.find(p => p.id === i.productId)?.originalPrice ?? 0), 0) - total).toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-gray-600">
            <span>Delivery Charges</span>
            <span className="text-green-600 font-medium">FREE</span>
          </div>
          <div className="border-t border-gray-100 pt-2 flex justify-between font-black text-gray-900 text-base">
            <span>Total Amount</span>
            <span>₹{total.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-100 px-4 py-3 z-40">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-black text-gray-900">₹{total.toLocaleString()}</span>
          <span className="text-xs text-green-600 font-medium">You save ₹{(activeItems.reduce((s, i) => s + (PRODUCTS.find(p => p.id === i.productId)?.originalPrice ?? 0), 0) - total).toLocaleString()}</span>
        </div>
        <button
          onClick={handlePlaceOrder}
          className="w-full py-3.5 rounded-xl bg-pink-600 text-white font-bold text-sm shadow hover:bg-pink-700 transition-colors"
        >
          PLACE ORDER
        </button>
        <button
          onClick={onContinueShopping}
          className="w-full mt-2 py-2 text-xs text-gray-500 font-medium"
        >
          Continue Shopping
        </button>
      </div>
    </div>
  )
}
