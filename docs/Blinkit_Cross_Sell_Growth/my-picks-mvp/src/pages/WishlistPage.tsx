import React, { useState } from 'react'
import { Heart, Star } from 'lucide-react'
import { PRODUCTS } from '../data/products'
import { useAppStore } from '../state/StoreContext'
import type { Intent, WishlistItem } from '../types'
import { INTENT_META } from '../types'
import IntentBottomSheet from '../components/IntentBottomSheet'
import Toast from '../components/Toast'

interface Props {
  onProductClick: (productId: string) => void
  onAddToBag: (productId: string) => void
}

type IntentFilter = 'all' | Intent

const INTENT_TABS: { id: IntentFilter; label: string; emoji?: string }[] = [
  { id: 'all', label: 'Recently Added' },
  { id: 'BUY_SOON', label: 'Buy Soon', emoji: '🔥' },
  { id: 'WAITING_FOR_PRICE', label: 'Price Drop', emoji: '💰' },
  { id: 'COMPARING', label: 'Comparing', emoji: '👀' },
  { id: 'JUST_SAVING', label: 'Just Saving', emoji: '✨' },
]

const INTENT_DESCRIPTIONS: Record<Intent, string> = {
  BUY_SOON: "Items you told us you may want to buy soon.",
  WAITING_FOR_PRICE: "Items you're keeping an eye on before buying.",
  COMPARING: "Products you're considering alongside other options.",
  JUST_SAVING: "Styles you're keeping for inspiration or later.",
}

export default function WishlistPage({ onProductClick, onAddToBag }: Props) {
  const { wishlist, removeFromWishlist } = useAppStore()
  const [activeFilter, setActiveFilter] = useState<IntentFilter>('all')
  const [intentSheet, setIntentSheet] = useState<{ productId: string; mode: 'save' | 'change' } | null>(null)
  const [toast, setToast] = useState<{ intent: Intent; mode: 'added' | 'updated' } | null>(null)

  const filteredItems: WishlistItem[] = wishlist
    .filter((item: WishlistItem) => {
      if (activeFilter === 'all') return true
      return item.intent === activeFilter
    })
    .sort((a: WishlistItem, b: WishlistItem) =>
      new Date(b.intentUpdatedAt ?? b.savedAt).getTime() -
      new Date(a.intentUpdatedAt ?? a.savedAt).getTime()
    )

  const getCount = (intent: IntentFilter) => {
    if (intent === 'all') return wishlist.length
    return wishlist.filter((i: WishlistItem) => i.intent === intent).length
  }

  const handleIntentClose = () => {
    const prev = intentSheet
    setIntentSheet(null)
    if (prev?.mode === 'change') {
      setTimeout(() => {
        const item = wishlist.find((i: WishlistItem) => i.productId === prev.productId)
        if (item?.intent) {
          setToast({ intent: item.intent, mode: 'updated' })
          setTimeout(() => setToast(null), 3000)
        }
      }, 150)
    }
  }

  if (wishlist.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] px-8 text-center pb-20">
        <Heart size={52} className="text-gray-200 mb-4" />
        <h2 className="text-lg font-bold text-gray-700">Your Wishlist is empty</h2>
        <p className="text-sm text-gray-400 mt-2">Save items you love to your Wishlist and buy them when you're ready.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col pb-20 min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white sticky top-0 z-30 px-4 pt-4 pb-0 shadow-sm">
        <div className="flex items-center justify-between mb-1">
          <div>
            <h1 className="text-lg font-black text-gray-900">My Picks</h1>
            <p className="text-xs text-gray-500">Your saved styles, organised by what you're looking for.</p>
          </div>
          <span className="text-xs text-gray-400">{wishlist.length} items</span>
        </div>

        {/* Filter chips */}
        <div className="flex gap-2 overflow-x-auto pb-3 mt-2" style={{ scrollbarWidth: 'none' }}>
          {INTENT_TABS.map(tab => {
            const count = getCount(tab.id)
            const isActive = activeFilter === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveFilter(tab.id)}
                className={`flex-shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                  isActive
                    ? 'bg-pink-600 text-white border-pink-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-pink-300'
                }`}
              >
                {tab.emoji && <span>{tab.emoji}</span>}
                {tab.label}
                {count > 0 && (
                  <span className={`ml-0.5 ${isActive ? 'text-pink-200' : 'text-gray-400'}`}>({count})</span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Context banner for specific intent */}
      {activeFilter !== 'all' && (
        <div className={`mx-4 mt-3 p-3 rounded-xl border ${INTENT_META[activeFilter].bg}`}>
          <p className={`text-xs font-semibold ${INTENT_META[activeFilter].color}`}>
            {INTENT_META[activeFilter].emoji} {INTENT_META[activeFilter].label}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">{INTENT_DESCRIPTIONS[activeFilter]}</p>
        </div>
      )}

      {/* Empty state */}
      {filteredItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 px-8 text-center">
          <span className="text-4xl mb-3">
            {activeFilter !== 'all' ? INTENT_META[activeFilter].emoji : '🛍️'}
          </span>
          <p className="text-sm font-semibold text-gray-600">Nothing here yet.</p>
          <p className="text-xs text-gray-400 mt-1">Save an item and tell us what you're saving it for.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 px-4 mt-3">
          {filteredItems.map((item: WishlistItem) => {
            const product = PRODUCTS.find(p => p.id === item.productId)
            if (!product) return null
            const intentMeta = item.intent ? INTENT_META[item.intent] : null
            const savedDaysAgo = Math.floor((Date.now() - new Date(item.savedAt).getTime()) / 86400000)

            return (
              <div
                key={item.productId}
                className="bg-white rounded-xl overflow-hidden shadow-sm border border-gray-50 cursor-pointer active:scale-[0.98] transition-transform"
                onClick={() => onProductClick(product.id)}
              >
                {/* Image */}
                <div className="relative bg-gray-100 overflow-hidden" style={{ aspectRatio: '3/4' }}>
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const t = e.target as HTMLImageElement
                      t.src = `https://placehold.co/300x400/f3f4f6/9ca3af?text=${encodeURIComponent(product.brand)}`
                    }}
                  />
                  <span className="absolute top-2 left-2 bg-pink-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded">
                    {product.discount}% OFF
                  </span>
                  <button
                    onClick={e => { e.stopPropagation(); removeFromWishlist(item.productId) }}
                    className="absolute top-2 right-2 w-7 h-7 bg-white rounded-full shadow flex items-center justify-center"
                  >
                    <Heart size={14} fill="#db2777" className="text-pink-600" />
                  </button>
                  {intentMeta && (
                    <span className={`absolute bottom-2 left-2 text-[9px] font-bold px-1.5 py-0.5 rounded-full border ${intentMeta.bg} ${intentMeta.color}`}>
                      {intentMeta.emoji} {intentMeta.short}
                    </span>
                  )}
                  {item.intent === 'WAITING_FOR_PRICE' && (
                    <span className="absolute bottom-2 right-2 bg-green-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full">
                      ₹{Math.floor(product.price * 0.08)} drop
                    </span>
                  )}
                </div>

                {/* Info */}
                <div className="p-2.5">
                  <p className="text-[10px] text-gray-400 font-semibold uppercase">{product.brand}</p>
                  <p className="text-xs text-gray-800 font-medium leading-tight mt-0.5 line-clamp-2">{product.name}</p>
                  <div className="flex items-center gap-1 mt-1.5">
                    <span className="text-sm font-bold text-gray-900">₹{product.price.toLocaleString()}</span>
                    <span className="text-xs text-gray-400 line-through">₹{product.originalPrice.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <Star size={10} fill="#fbbf24" className="text-amber-400" />
                    <span className="text-[10px] text-gray-500">{product.rating}</span>
                    <span className="text-[9px] text-gray-300 ml-auto">Saved {savedDaysAgo}d ago</span>
                  </div>
                  <button
                    onClick={e => { e.stopPropagation(); onAddToBag(product.id) }}
                    className="mt-2 w-full py-1.5 rounded-lg border border-pink-500 text-pink-600 text-[11px] font-bold hover:bg-pink-50 transition-colors"
                  >
                    ADD TO BAG
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {intentSheet && (
        <IntentBottomSheet
          productId={intentSheet.productId}
          mode={intentSheet.mode}
          onClose={handleIntentClose}
        />
      )}
      {toast && <Toast intent={toast.intent} mode={toast.mode} />}
    </div>
  )
}
