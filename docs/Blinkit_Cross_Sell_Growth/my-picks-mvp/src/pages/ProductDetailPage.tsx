import React, { useState } from 'react'
import { ChevronLeft, Heart, Star, ShoppingBag, Truck, RotateCcw } from 'lucide-react'
import { Product, INTENT_META, Intent } from '../types'
import { useAppStore } from '../state/StoreContext'
import IntentBottomSheet from '../components/IntentBottomSheet'
import Toast from '../components/Toast'

interface Props {
  product: Product
  onBack: () => void
  onAddToBag: (size: string) => void
  fromContextual?: boolean
}

export default function ProductDetailPage({ product, onBack, onAddToBag, fromContextual }: Props) {
  const { isWishlisted, addToWishlist, removeFromWishlist, getWishlistItem, logEvent } = useAppStore()
  const [selectedSize, setSelectedSize] = useState<string | null>(null)
  const [showIntentSheet, setShowIntentSheet] = useState(false)
  const [intentMode, setIntentMode] = useState<'save' | 'change'>('save')
  const [toast, setToast] = useState<{ intent: Intent; mode: 'added' | 'updated' } | null>(null)
  const [imgIndex, setImgIndex] = useState(0)
  const [addedToBag, setAddedToBag] = useState(false)

  const wishlisted = isWishlisted(product.id)
  const wishlistItem = getWishlistItem(product.id)
  const intentMeta = wishlistItem?.intent ? INTENT_META[wishlistItem.intent] : null

  const images = [product.image]

  const handleHeart = () => {
    if (wishlisted) {
      removeFromWishlist(product.id)
    } else {
      addToWishlist(product.id)
      setIntentMode('save')
      setShowIntentSheet(true)
      logEvent('INTENT_PROMPT_SHOWN', product.id)
    }
  }

  const handleIntentClose = () => {
    setShowIntentSheet(false)
    // Check if intent was set (via wishlist update)
    setTimeout(() => {
      const item = getWishlistItem(product.id)
      if (item?.intent) {
        setToast({ intent: item.intent, mode: intentMode === 'save' ? 'added' : 'updated' })
        setTimeout(() => setToast(null), 3000)
      }
    }, 100)
  }

  const handleAddToBag = () => {
    if (!selectedSize) {
      // Auto-select first size for demo
      setSelectedSize(product.sizes[0])
    }
    setAddedToBag(true)
    onAddToBag(selectedSize ?? product.sizes[0])
  }

  return (
    <div className="flex flex-col pb-24 min-h-screen bg-white">
      {/* Top Nav */}
      <div className="sticky top-0 z-30 bg-white flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <button onClick={onBack} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors">
          <ChevronLeft size={22} className="text-gray-700" />
        </button>
        <div className="flex items-center gap-2">
          <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors">
            <ShoppingBag size={18} className="text-gray-600" />
          </button>
          <button
            onClick={handleHeart}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
          >
            <Heart size={18} fill={wishlisted ? '#db2777' : 'none'} className={wishlisted ? 'text-pink-600' : 'text-gray-600'} />
          </button>
        </div>
      </div>

      {/* Product Images */}
      <div className="relative bg-gray-50 aspect-[4/5] overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            ;(e.target as HTMLImageElement).src = `https://via.placeholder.com/400x500/f3f4f6/9ca3af?text=${encodeURIComponent(product.name)}`
          }}
        />
        {/* Discount badge */}
        <div className="absolute top-3 left-3 bg-pink-600 text-white text-xs font-bold px-2 py-0.5 rounded">
          {product.discount}% OFF
        </div>
        {/* Contextual label */}
        {fromContextual && intentMeta && (
          <div className="absolute bottom-3 left-3">
            <div className={`text-xs font-semibold px-2 py-1 rounded-lg border ${intentMeta.bg} ${intentMeta.color} shadow-sm`}>
              {intentMeta.emoji} {intentMeta.short} • You saved this with My Picks
            </div>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="px-4 pt-4">
        <p className="text-xs text-gray-500 uppercase font-bold tracking-widest">{product.brand}</p>
        <h1 className="text-lg font-semibold text-gray-900 mt-1">{product.name}</h1>

        <div className="flex items-center gap-2 mt-2">
          <span className="text-xl font-black text-gray-900">₹{product.price.toLocaleString()}</span>
          <span className="text-sm text-gray-400 line-through">₹{product.originalPrice.toLocaleString()}</span>
          <span className="text-sm font-bold text-green-600">{product.discount}% off</span>
        </div>

        <div className="flex items-center gap-1.5 mt-2">
          <div className="flex items-center gap-1 bg-green-600 text-white text-xs font-bold px-1.5 py-0.5 rounded">
            <Star size={10} fill="white" />
            {product.rating}
          </div>
          <span className="text-xs text-gray-500">{product.ratingsCount.toLocaleString()} Ratings</span>
        </div>

        {/* My Pick indicator */}
        {intentMeta && wishlistItem && (
          <div className={`mt-3 flex items-center justify-between px-3 py-2.5 rounded-xl border ${intentMeta.bg}`}>
            <div className="flex items-center gap-2">
              <span className="text-base">{intentMeta.emoji}</span>
              <div>
                <p className={`text-xs font-bold ${intentMeta.color}`}>{intentMeta.label}</p>
                <p className="text-[10px] text-gray-500">My Pick</p>
              </div>
            </div>
            <button
              onClick={() => { setIntentMode('change'); setShowIntentSheet(true) }}
              className="text-xs text-pink-600 font-semibold underline underline-offset-2"
            >
              Change
            </button>
          </div>
        )}

        {/* Sizes */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold text-gray-800">Select Size</p>
            <button className="text-xs text-pink-600 underline">Size Guide</button>
          </div>
          <div className="flex gap-2 flex-wrap">
            {product.sizes.map(size => (
              <button
                key={size}
                onClick={() => setSelectedSize(size)}
                className={`border rounded-full px-3 py-1.5 text-sm font-medium transition-all ${
                  selectedSize === size
                    ? 'border-pink-600 text-pink-600 bg-pink-50'
                    : 'border-gray-200 text-gray-600 hover:border-pink-300'
                }`}
              >
                {size}
              </button>
            ))}
          </div>
        </div>

        {/* Delivery info */}
        <div className="mt-4 space-y-2">
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Truck size={14} className="text-gray-400" />
            <span>Free delivery on orders above ₹999</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <RotateCcw size={14} className="text-gray-400" />
            <span>14-day easy return & exchange</span>
          </div>
        </div>

        {/* Product info */}
        <div className="mt-4 p-3 bg-gray-50 rounded-xl">
          <p className="text-xs font-semibold text-gray-700 mb-1.5">Product Details</p>
          <p className="text-xs text-gray-500 leading-relaxed">
            {product.category} • Premium quality fabric • Comfortable fit designed for everyday wear.
            Crafted with attention to detail for a sophisticated look.
          </p>
        </div>
      </div>

      {/* Bottom CTAs */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-100 px-4 py-3 flex gap-2 z-30">
        <button
          onClick={handleHeart}
          className={`flex-none w-12 h-12 rounded-xl border flex items-center justify-center transition-colors ${
            wishlisted ? 'border-pink-500 bg-pink-50' : 'border-gray-200'
          }`}
        >
          <Heart size={20} fill={wishlisted ? '#db2777' : 'none'} className={wishlisted ? 'text-pink-600' : 'text-gray-500'} />
        </button>
        <button
          onClick={handleAddToBag}
          className="flex-1 h-12 rounded-xl bg-pink-600 hover:bg-pink-700 text-white font-bold text-sm transition-colors flex items-center justify-center gap-2"
        >
          <ShoppingBag size={16} />
          {addedToBag ? 'ADDED TO BAG' : 'ADD TO BAG'}
        </button>
      </div>

      {/* Intent Sheet */}
      {showIntentSheet && (
        <IntentBottomSheet
          productId={product.id}
          mode={intentMode}
          onClose={handleIntentClose}
        />
      )}

      {/* Toast */}
      {toast && <Toast intent={toast.intent} mode={toast.mode} />}
    </div>
  )
}
