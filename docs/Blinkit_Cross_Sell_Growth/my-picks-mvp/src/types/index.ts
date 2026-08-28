export type Intent = string

export interface Category {
  id: string
  emoji: string
  label: string
  short: string
  description: string
  color: string
  bg: string
  isCustom?: boolean
}

export interface Product {
  id: string
  brand: string
  name: string
  category: string
  price: number
  originalPrice: number
  discount: number
  rating: number
  ratingsCount: number
  image: string
  sizes: string[]
}

export interface WishlistItem {
  productId: string
  savedAt: string
  intent: Intent | null
  intentUpdatedAt?: string
}

export interface CartItem {
  productId: string
  size: string
  addedAt: string
  purchasedAt?: string
}

export interface AnalyticsEvent {
  type: string
  timestamp: string
  productId?: string
  intent?: Intent | null
}

// ── Intent Meta ────────────────────────────────────────────────────────────

export const DEFAULT_CATEGORIES: Category[] = [
  {
    id: 'BUY_SOON',
    emoji: '🔥', label: 'Buy Soon', short: 'Buy Soon',
    description: "I'm likely to buy this soon.",
    color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200',
  },
  {
    id: 'WAITING_FOR_PRICE',
    emoji: '💰', label: 'Waiting for Price', short: 'Waiting for Price',
    description: "I like it, but I'm waiting for a better price.",
    color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200',
  },
  {
    id: 'COMPARING',
    emoji: '👀', label: 'Comparing', short: 'Comparing',
    description: "I'm considering this with other options.",
    color: 'text-purple-600', bg: 'bg-purple-50 border-purple-200',
  },
  {
    id: 'JUST_SAVING',
    emoji: '✨', label: 'Just Saving', short: 'Just Saving',
    description: "I like it and want to keep it for later.",
    color: 'text-green-600', bg: 'bg-green-50 border-green-200',
  },
]

export const INTENT_META: Record<string, { emoji: string; label: string; short: string; description: string; color: string; bg: string }> = {
  BUY_SOON: DEFAULT_CATEGORIES[0],
  WAITING_FOR_PRICE: DEFAULT_CATEGORIES[1],
  COMPARING: DEFAULT_CATEGORIES[2],
  JUST_SAVING: DEFAULT_CATEGORIES[3],
}

export const INTENT_PRIORITY: string[] = ['BUY_SOON', 'WAITING_FOR_PRICE', 'COMPARING', 'JUST_SAVING']
