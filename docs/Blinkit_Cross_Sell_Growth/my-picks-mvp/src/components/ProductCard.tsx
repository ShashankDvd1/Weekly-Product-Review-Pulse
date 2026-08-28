import React from 'react'
import { Heart, Star } from 'lucide-react'
import { Product } from '../types'
import { INTENT_META } from '../types'
import { useAppStore } from '../state/StoreContext'

interface Props {
  product: Product
  onClick: () => void
  showAddToBag?: boolean
  onAddToBag?: () => void
  onHeartSave?: (productId: string) => void
}

export default function ProductCard({ product, onClick, showAddToBag, onAddToBag, onHeartSave }: Props) {
  const { isWishlisted, addToWishlist, removeFromWishlist, getWishlistItem, categories } = useAppStore()
  const wishlisted = isWishlisted(product.id)
  const wishlistItem = getWishlistItem(product.id)
  const intentMeta = wishlistItem?.intent ? categories.find(c => c.id === wishlistItem.intent) : null

  const handleHeartClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (wishlisted) {
      removeFromWishlist(product.id)
    } else {
      addToWishlist(product.id)
      if (onHeartSave) {
        onHeartSave(product.id)
      }
    }
  }

  return (
    <div
      className="bg-white rounded-xl overflow-hidden shadow-sm border border-gray-50 cursor-pointer active:scale-[0.98] transition-transform"
      onClick={onClick}
    >
      {/* Image */}
      <div className="relative aspect-[3/4] bg-gray-100 overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-full object-cover"
          loading="lazy"
          onError={(e) => {
            ;(e.target as HTMLImageElement).src = `https://via.placeholder.com/300x400/f3f4f6/9ca3af?text=${encodeURIComponent(product.brand)}`
          }}
        />
        {/* Discount badge */}
        <div className="absolute top-2 left-2 bg-pink-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded">
          {product.discount}% OFF
        </div>
        {/* Heart */}
        <button
          onClick={handleHeartClick}
          className="absolute top-2 right-2 w-8 h-8 bg-white rounded-full shadow flex items-center justify-center"
        >
          <Heart size={16} fill={wishlisted ? '#db2777' : 'none'} className={wishlisted ? 'text-pink-600' : 'text-gray-400'} />
        </button>
        {/* Intent badge */}
        {intentMeta && (
          <div className={`absolute bottom-2 left-2 text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${intentMeta.bg} ${intentMeta.color}`}>
            {intentMeta.emoji} {intentMeta.short}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-2.5">
        <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wide">{product.brand}</p>
        <p className="text-xs text-gray-800 font-medium leading-tight mt-0.5 line-clamp-2">{product.name}</p>
        <div className="flex items-center gap-1.5 mt-1.5">
          <span className="text-sm font-bold text-gray-900">₹{product.price.toLocaleString()}</span>
          <span className="text-xs text-gray-400 line-through">₹{product.originalPrice.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1 mt-1">
          <Star size={10} fill="#fbbf24" className="text-amber-400" />
          <span className="text-[10px] text-gray-600">{product.rating} ({(product.ratingsCount / 1000).toFixed(1)}k)</span>
        </div>

        {showAddToBag && (
          <button
            onClick={e => { e.stopPropagation(); onAddToBag?.() }}
            className="mt-2 w-full py-1.5 rounded-lg border border-pink-500 text-pink-600 text-xs font-semibold hover:bg-pink-50 transition-colors"
          >
            ADD TO BAG
          </button>
        )}
      </div>
    </div>
  )
}
