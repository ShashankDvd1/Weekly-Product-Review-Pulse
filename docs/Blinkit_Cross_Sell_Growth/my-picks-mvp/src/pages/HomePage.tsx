import React, { useState } from 'react'
import { ShoppingBag, Bell, Search, ChevronRight } from 'lucide-react'
import { PRODUCTS } from '../data/products'
import { useAppStore } from '../state/StoreContext'
import ProductCard from '../components/ProductCard'
import ContextualReentryCard from '../components/ContextualReentryCard'
import IntentBottomSheet from '../components/IntentBottomSheet'

interface Props {
  onProductClick: (productId: string) => void
  onViewMyPicks: () => void
  onAddToBag: (productId: string) => void
}

const BANNER_CATEGORIES = [
  { label: 'Dresses', emoji: '👗' },
  { label: 'Shirts', emoji: '👔' },
  { label: 'Sneakers', emoji: '👟' },
  { label: 'Bags', emoji: '👜' },
  { label: 'Kurtas', emoji: '🪷' },
  { label: 'Jackets', emoji: '🧥' },
]

export default function HomePage({ onProductClick, onViewMyPicks, onAddToBag }: Props) {
  const { wishlist, addToWishlist, analytics } = useAppStore()
  const [intentSheet, setIntentSheet] = useState<string | null>(null)

  const wishlistItemsWithIntent = wishlist.filter(item => item.intent !== null)
  const sortedWishlistItems = [...wishlistItemsWithIntent].sort((a, b) => {
    const priority = ['BUY_SOON', 'WAITING_FOR_PRICE', 'COMPARING', 'JUST_SAVING']
    const aIndex = priority.indexOf(a.intent || '')
    const bIndex = priority.indexOf(b.intent || '')
    const aVal = aIndex === -1 ? 99 : aIndex
    const bVal = bIndex === -1 ? 99 : bIndex
    return aVal - bVal
  })

  const handleProductClick = (productId: string) => {
    onProductClick(productId)
  }

  const handleIntentClose = () => {
    setIntentSheet(null)
  }

  return (
    <div className="flex flex-col pb-20 min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white sticky top-0 z-30 shadow-sm">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="flex-1">
            <div className="flex items-center gap-1">
              <span className="text-pink-600 font-extrabold text-xl tracking-tight">myntra</span>
              <span className="text-[9px] text-gray-400 border border-gray-200 rounded px-1 ml-1 font-medium">MVP</span>
            </div>
          </div>
          <Bell size={20} className="text-gray-500" />
          <div className="relative cursor-pointer" onClick={() => {}}>
            <ShoppingBag size={20} className="text-gray-500" />
            {analytics.cartCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-pink-600 rounded-full text-white text-[9px] flex items-center justify-center font-bold">
                {analytics.cartCount}
              </span>
            )}
          </div>
        </div>
        {/* Search bar */}
        <div className="px-4 pb-3">
          <div className="flex items-center gap-2 bg-gray-100 rounded-full px-3 py-2">
            <Search size={14} className="text-gray-400" />
            <span className="text-sm text-gray-400">Search for brands, products...</span>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <div className="mx-4 mt-4 rounded-2xl overflow-hidden bg-gradient-to-r from-pink-600 to-pink-400 h-36 flex items-center justify-between px-5">
        <div>
          <p className="text-white font-black text-2xl leading-tight">END OF<br />SEASON</p>
          <p className="text-pink-100 text-xs mt-1">Up to 80% Off on Fashion</p>
          <button className="mt-2 bg-white text-pink-600 text-xs font-bold px-3 py-1.5 rounded-full">
            SHOP NOW
          </button>
        </div>
        <div className="text-6xl">👗</div>
      </div>

      {/* Category Shortcuts */}
      <div className="mt-4 px-4">
        <div className="flex gap-3 overflow-x-auto no-scrollbar pb-1">
          {BANNER_CATEGORIES.map(cat => (
            <div key={cat.label} className="flex flex-col items-center gap-1 flex-shrink-0">
              <div className="w-12 h-12 rounded-full bg-white shadow-sm border border-gray-100 flex items-center justify-center text-2xl">
                {cat.emoji}
              </div>
              <span className="text-[10px] text-gray-600 font-medium">{cat.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* My Picks Contextual Re-entry Slider */}
      {sortedWishlistItems.length > 0 && (
        <div className="mt-5">
          <div className="px-4 mb-2 flex items-center justify-between">
            <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">My Picks</span>
            <button onClick={onViewMyPicks} className="text-xs text-pink-600 font-semibold hover:underline">
              View all ({sortedWishlistItems.length})
            </button>
          </div>
          <div className="flex gap-3 overflow-x-auto px-4 pb-3 no-scrollbar snap-x snap-mandatory scroll-smooth">
            {sortedWishlistItems.map(item => {
              const product = PRODUCTS.find(p => p.id === item.productId)
              if (!product) return null
              return (
                <div key={item.productId} className="w-[85vw] max-w-[340px] flex-shrink-0 snap-center transition-transform duration-200 active:scale-[0.99] animate-slide-in">
                  <ContextualReentryCard
                    product={product}
                    intent={item.intent!}
                    onAddToBag={() => onAddToBag(product.id)}
                    onViewMyPicks={onViewMyPicks}
                  />
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Product Recommendations */}
      <div className="mt-5 px-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-gray-900">Recommended For You</h2>
          <button className="flex items-center gap-0.5 text-xs text-pink-600 font-medium">
            View all <ChevronRight size={12} />
          </button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {PRODUCTS.map(product => (
            <ProductCard
              key={product.id}
              product={product}
              onClick={() => handleProductClick(product.id)}
              onHeartSave={setIntentSheet}
            />
          ))}
        </div>
      </div>

      {/* Intent Sheet */}
      {intentSheet && (
        <IntentBottomSheet
          productId={intentSheet}
          onClose={() => setIntentSheet(null)}
        />
      )}
    </div>
  )
}
