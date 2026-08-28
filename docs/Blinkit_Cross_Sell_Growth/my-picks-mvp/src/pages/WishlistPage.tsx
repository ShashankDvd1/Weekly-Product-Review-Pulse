import React, { useState } from 'react'
import { Heart, Star, Plus, Edit2, Trash2 } from 'lucide-react'
import { PRODUCTS } from '../data/products'
import { useAppStore } from '../state/StoreContext'
import type { Intent, WishlistItem } from '../types'
import IntentBottomSheet from '../components/IntentBottomSheet'
import Toast from '../components/Toast'

interface Props {
  onProductClick: (productId: string) => void
  onAddToBag: (productId: string) => void
}

type IntentFilter = 'all' | Intent

export default function WishlistPage({ onProductClick, onAddToBag }: Props) {
  const { wishlist, removeFromWishlist, categories, addCategory, editCategory, deleteCategory } = useAppStore()
  const [activeFilter, setActiveFilter] = useState<IntentFilter>('all')
  const [intentSheet, setIntentSheet] = useState<{ productId: string; mode: 'save' | 'change' } | null>(null)
  const [toast, setToast] = useState<{ intent: Intent; mode: 'added' | 'updated' } | null>(null)
  
  // Category Modal State
  const [catModal, setCatModal] = useState<{ id?: string; emoji: string; label: string; description: string } | null>(null)

  const tabs = [
    { id: 'all' as IntentFilter, label: 'Recently Added' },
    ...categories.map(c => ({ id: c.id as IntentFilter, label: c.label, emoji: c.emoji }))
  ]

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

  const selectedCategory = categories.find(c => c.id === activeFilter)

  const handleSaveCategory = (e: React.FormEvent) => {
    e.preventDefault()
    if (!catModal) return
    if (catModal.id) {
      editCategory(catModal.id, catModal.emoji || '✨', catModal.label, catModal.description)
    } else {
      addCategory(catModal.emoji || '✨', catModal.label, catModal.description)
    }
    setCatModal(null)
  }

  const handleDeleteCategory = (id: string) => {
    if (window.confirm("Are you sure you want to delete this custom category? Saved items will be moved back to standard wishlist.")) {
      deleteCategory(id)
      setActiveFilter('all')
    }
  }

  if (wishlist.length === 0 && categories.length === 4) {
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

        {/* Filter chips & Add button */}
        <div className="flex items-center gap-2 overflow-x-auto pb-3 mt-2 no-scrollbar">
          {tabs.map(tab => {
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
          
          <button
            onClick={() => setCatModal({ emoji: '✨', label: '', description: '' })}
            className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full border border-dashed border-gray-300 text-gray-400 hover:border-pink-500 hover:text-pink-600 bg-white"
            title="Create Custom Category"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Context banner / controls for selected category */}
      {selectedCategory && (
        <div className={`mx-4 mt-3 p-3 rounded-xl border flex items-center justify-between gap-3 ${selectedCategory.bg || 'bg-pink-50 border-pink-200'}`}>
          <div className="flex-1">
            <p className={`text-xs font-bold ${selectedCategory.color || 'text-pink-600'}`}>
              {selectedCategory.emoji} {selectedCategory.label}
            </p>
            <p className="text-[11px] text-gray-500 mt-0.5">{selectedCategory.description}</p>
          </div>
          {selectedCategory.isCustom && (
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <button
                onClick={() => setCatModal({ id: selectedCategory.id, emoji: selectedCategory.emoji, label: selectedCategory.label, description: selectedCategory.description })}
                className="w-7 h-7 bg-white rounded-full flex items-center justify-center border border-gray-200 text-gray-500 hover:text-pink-600 shadow-sm"
              >
                <Edit2 size={12} />
              </button>
              <button
                onClick={() => handleDeleteCategory(selectedCategory.id)}
                className="w-7 h-7 bg-white rounded-full flex items-center justify-center border border-gray-200 text-gray-500 hover:text-red-600 shadow-sm"
              >
                <Trash2 size={12} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {filteredItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 px-8 text-center">
          <span className="text-4xl mb-3">
            {selectedCategory ? selectedCategory.emoji : '🛍️'}
          </span>
          <p className="text-sm font-semibold text-gray-600">Nothing here yet.</p>
          <p className="text-xs text-gray-400 mt-1">Save an item and tell us what you're saving it for.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 px-4 mt-3">
          {filteredItems.map((item: WishlistItem) => {
            const product = PRODUCTS.find(p => p.id === item.productId)
            if (!product) return null
            const intentMeta = item.intent ? categories.find(c => c.id === item.intent) : null
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

      {/* Category Creation / Edit Modal */}
      {catModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4" onClick={() => setCatModal(null)}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-xs" />
          <form 
            onSubmit={handleSaveCategory}
            className="relative bg-white rounded-2xl w-full max-w-sm p-5 shadow-2xl flex flex-col gap-4"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="font-bold text-lg text-gray-900">
              {catModal.id ? 'Edit Category' : 'Create Custom Category'}
            </h3>
            
            <div className="flex gap-2.5">
              <div className="flex flex-col gap-1 w-14">
                <label className="text-[10px] text-gray-400 font-bold uppercase">Emoji</label>
                <input 
                  type="text" 
                  value={catModal.emoji}
                  onChange={e => setCatModal({ ...catModal, emoji: e.target.value })}
                  maxLength={2}
                  className="border border-gray-200 rounded-xl p-2 text-center text-xl bg-gray-50"
                  required
                />
              </div>
              <div className="flex-1 flex flex-col gap-1">
                <label className="text-[10px] text-gray-400 font-bold uppercase">Name / Label</label>
                <input 
                  type="text" 
                  value={catModal.label}
                  onChange={e => setCatModal({ ...catModal, label: e.target.value })}
                  placeholder="e.g. Winter Wear"
                  className="border border-gray-200 rounded-xl p-2 text-sm bg-gray-50"
                  required
                />
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-400 font-bold uppercase">Description / Intent</label>
              <textarea 
                value={catModal.description}
                onChange={e => setCatModal({ ...catModal, description: e.target.value })}
                placeholder="Why are you saving items to this category?"
                className="border border-gray-200 rounded-xl p-2 text-sm bg-gray-50 resize-none h-20"
                required
              />
            </div>

            <div className="flex gap-2 mt-2">
              <button 
                type="button"
                onClick={() => setCatModal(null)}
                className="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-500 font-semibold text-xs"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="flex-1 py-2.5 rounded-xl bg-pink-600 text-white font-semibold text-xs hover:bg-pink-700"
              >
                Save
              </button>
            </div>
          </form>
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
