import { useState, useCallback } from 'react'
import type { WishlistItem, CartItem, Intent, AnalyticsEvent } from '../types'
import { DEMO_WISHLIST, PRODUCTS } from '../data/products'

const WISHLIST_KEY = 'my_picks_wishlist'
const CART_KEY = 'my_picks_cart'
const EVENTS_KEY = 'my_picks_events'
const SIM_DATE_KEY = 'my_picks_sim_date_offset'

function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (raw) return JSON.parse(raw) as T
  } catch { /* empty */ }
  return fallback
}

function save<T>(key: string, value: T) {
  localStorage.setItem(key, JSON.stringify(value))
}

export function useStore() {
  const [wishlist, setWishlistState] = useState<WishlistItem[]>(() =>
    load<WishlistItem[]>(WISHLIST_KEY, DEMO_WISHLIST)
  )
  const [cart, setCartState] = useState<CartItem[]>(() => load<CartItem[]>(CART_KEY, []))
  const [events, setEvents] = useState<AnalyticsEvent[]>(() => load<AnalyticsEvent[]>(EVENTS_KEY, []))
  const [simDateOffsetDays, setSimDateOffsetDays] = useState<number>(() => load<number>(SIM_DATE_KEY, 0))

  const setWishlist = useCallback((items: WishlistItem[] | ((prev: WishlistItem[]) => WishlistItem[])) => {
    setWishlistState(prev => {
      const next = typeof items === 'function' ? items(prev) : items
      save(WISHLIST_KEY, next)
      return next
    })
  }, [])

  const setCart = useCallback((items: CartItem[]) => {
    setCartState(items)
    save(CART_KEY, items)
  }, [])

  const logEvent = useCallback((type: string, productId?: string, intent?: Intent | null) => {
    const ev: AnalyticsEvent = { type, timestamp: new Date().toISOString(), productId, intent }
    setEvents(prev => {
      const next = [...prev, ev]
      save(EVENTS_KEY, next)
      return next
    })
  }, [])

  // Wishlist actions
  const addToWishlist = useCallback((productId: string) => {
    setWishlist(prev => {
      if (prev.find((i: WishlistItem) => i.productId === productId)) return prev
      return [...prev, { productId, savedAt: new Date().toISOString(), intent: null }]
    })
    logEvent('WISHLIST_ADDED', productId)
  }, [setWishlist, logEvent])

  const removeFromWishlist = useCallback((productId: string) => {
    setWishlist(prev => prev.filter((i: WishlistItem) => i.productId !== productId))
  }, [setWishlist])

  const setIntent = useCallback((productId: string, intent: Intent) => {
    setWishlist(prev =>
      prev.map((i: WishlistItem) => i.productId === productId
        ? { ...i, intent, intentUpdatedAt: new Date().toISOString() }
        : i
      )
    )
    logEvent('INTENT_SELECTED', productId, intent)
  }, [setWishlist, logEvent])

  const clearIntent = useCallback((productId: string) => {
    setWishlist(prev =>
      prev.map((i: WishlistItem) => i.productId === productId
        ? { ...i, intent: null, intentUpdatedAt: undefined }
        : i
      )
    )
    logEvent('INTENT_SKIPPED', productId)
  }, [setWishlist, logEvent])

  const isWishlisted = useCallback((productId: string) =>
    wishlist.some((i: WishlistItem) => i.productId === productId), [wishlist])

  const getWishlistItem = useCallback((productId: string) =>
    wishlist.find((i: WishlistItem) => i.productId === productId) ?? null, [wishlist])

  // Cart actions
  const addToCart = useCallback((productId: string, size: string) => {
    setCart([...cart.filter((i: CartItem) => i.productId !== productId),
      { productId, size, addedAt: new Date().toISOString() }])
    logEvent('ADD_TO_BAG', productId)
  }, [cart, setCart, logEvent])

  const removeFromCart = useCallback((productId: string) => {
    setCart(cart.filter((i: CartItem) => i.productId !== productId))
  }, [cart, setCart])

  const placeOrder = useCallback(() => {
    const now = new Date().toISOString()
    const updated = cart.map((i: CartItem) => ({ ...i, purchasedAt: now }))
    setCart(updated)
    cart.forEach((i: CartItem) => logEvent('PURCHASE', i.productId))
    setTimeout(() => setCart([]), 2500)
  }, [cart, setCart, logEvent])

  // Contextual re-entry: highest priority intent item
  const getContextualProduct = useCallback(() => {
    const intents: Intent[] = ['BUY_SOON', 'WAITING_FOR_PRICE', 'COMPARING']
    for (const intent of intents) {
      const item = [...wishlist]
        .filter((i: WishlistItem) => i.intent === intent)
        .sort((a: WishlistItem, b: WishlistItem) =>
          new Date(b.intentUpdatedAt ?? b.savedAt).getTime() -
          new Date(a.intentUpdatedAt ?? a.savedAt).getTime()
        )[0]
      if (item) {
        const product = PRODUCTS.find(p => p.id === item.productId)
        if (product) return { product, item }
      }
    }
    return null
  }, [wishlist])

  // Analytics derived
  const analytics = {
    total: wishlist.length,
    withIntent: wishlist.filter((i: WishlistItem) => i.intent !== null).length,
    intentCaptureRate: wishlist.length
      ? Math.round((wishlist.filter((i: WishlistItem) => i.intent).length / wishlist.length) * 100)
      : 0,
    buySoon: wishlist.filter((i: WishlistItem) => i.intent === 'BUY_SOON').length,
    reEntries: events.filter((e: AnalyticsEvent) => e.type === 'PRODUCT_REVISITED').length,
    addToBag: events.filter((e: AnalyticsEvent) => e.type === 'ADD_TO_BAG').length,
    purchases: events.filter((e: AnalyticsEvent) => e.type === 'PURCHASE').length,
    cartCount: cart.filter((i: CartItem) => !i.purchasedAt).length,
    events,
  }

  // Demo controls
  const resetDemo = useCallback(() => {
    setWishlist(DEMO_WISHLIST)
    setCart([])
    setEvents([])
    setSimDateOffsetDays(0)
    save(SIM_DATE_KEY, 0)
  }, [setWishlist, setCart])

  const simulatePlus30Days = useCallback(() => {
    const newOffset = simDateOffsetDays + 30
    setSimDateOffsetDays(newOffset)
    save(SIM_DATE_KEY, newOffset)
  }, [simDateOffsetDays])

  const setAllBuySoon = useCallback(() => {
    setWishlist(wishlist.map((i: WishlistItem) => ({
      ...i,
      intent: 'BUY_SOON' as Intent,
      intentUpdatedAt: new Date().toISOString()
    })))
  }, [wishlist, setWishlist])

  return {
    wishlist, cart, analytics, simDateOffsetDays,
    addToWishlist, removeFromWishlist, setIntent, clearIntent,
    isWishlisted, getWishlistItem,
    addToCart, removeFromCart, placeOrder,
    getContextualProduct,
    logEvent,
    resetDemo, simulatePlus30Days, setAllBuySoon,
  }
}

export type Store = ReturnType<typeof useStore>
