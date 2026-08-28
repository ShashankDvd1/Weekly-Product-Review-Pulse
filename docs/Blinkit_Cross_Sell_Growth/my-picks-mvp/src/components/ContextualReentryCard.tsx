import React from 'react'
import { ChevronRight, ShoppingBag } from 'lucide-react'
import { Product } from '../types'
import { useAppStore } from '../state/StoreContext'

interface Props {
  product: Product
  intent: string
  onAddToBag: () => void
  onViewMyPicks: () => void
}

export default function ContextualReentryCard({ product, intent, onAddToBag, onViewMyPicks }: Props) {
  const { categories } = useAppStore()
  const meta = categories.find(c => c.id === intent) || { emoji: '🔥', label: intent, short: intent, bg: 'bg-orange-50 border-orange-200', color: 'text-orange-600' }

  return (
    <div className="mx-4 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-4 pt-4 pb-2 flex items-center justify-between">
        <div>
          <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">My Picks</p>
          <p className="text-sm font-semibold text-gray-800 mt-0.5">Still thinking about this? 👀</p>
        </div>
        <span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${meta.bg} ${meta.color}`}>
          {meta.emoji} {meta.short}
        </span>
      </div>

      {/* Product */}
      <div className="flex gap-3 px-4 pb-3">
        <img
          src={product.image}
          alt={product.name}
          className="w-16 h-20 object-cover rounded-xl bg-gray-100 flex-shrink-0"
          onError={(e) => {
            ;(e.target as HTMLImageElement).src = `https://via.placeholder.com/64x80/f3f4f6/9ca3af?text=${encodeURIComponent(product.brand[0])}`
          }}
        />
        <div className="flex-1 flex flex-col justify-between">
          <div>
            <p className="text-[10px] text-gray-500 font-semibold uppercase">{product.brand}</p>
            <p className="text-sm font-medium text-gray-800 leading-tight mt-0.5">{product.name}</p>
            <p className="text-sm font-bold text-gray-900 mt-1">₹{product.price.toLocaleString()}</p>
          </div>
          <p className={`text-[10px] font-semibold ${meta.color}`}>You saved this as {meta.emoji} {meta.short}</p>
        </div>
      </div>

      {/* CTAs */}
      <div className="grid grid-cols-2 border-t border-gray-100">
        <button
          onClick={onAddToBag}
          className="flex items-center justify-center gap-1.5 py-3 text-xs font-semibold text-white bg-pink-600 hover:bg-pink-700 transition-colors"
        >
          <ShoppingBag size={13} />
          ADD TO BAG
        </button>
        <button
          onClick={onViewMyPicks}
          className="flex items-center justify-center gap-1 py-3 text-xs font-medium text-pink-600 hover:bg-pink-50 transition-colors"
        >
          View My Picks <ChevronRight size={13} />
        </button>
      </div>
    </div>
  )
}
