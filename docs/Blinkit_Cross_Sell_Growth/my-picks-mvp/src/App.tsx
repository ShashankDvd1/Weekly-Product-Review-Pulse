import React, { useState } from 'react'
import { StoreProvider, useAppStore } from './state/StoreContext'
import BottomNavigation, { Tab } from './components/BottomNavigation'
import HomePage from './pages/HomePage'
import WishlistPage from './pages/WishlistPage'
import ProductDetailPage from './pages/ProductDetailPage'
import CartPage from './pages/CartPage'
import DemoPanel from './components/DemoPanel'
import Toast from './components/Toast'
import { Intent, INTENT_META } from './types'
import { PRODUCTS } from './data/products'

type View =
  | { screen: 'home' }
  | { screen: 'product'; productId: string; fromContextual?: boolean }
  | { screen: 'cart' }

function AppShell() {
  const { analytics, addToCart, getWishlistItem, wishlist } = useAppStore()
  const [activeTab, setActiveTab] = useState<Tab>('home')
  const [view, setView] = useState<View>({ screen: 'home' })
  const [toast, setToast] = useState<{ intent: Intent; mode: 'added' | 'updated' } | null>(null)
  const [addedToBagProduct, setAddedToBagProduct] = useState<string | null>(null)

  const showToast = (intent: Intent, mode: 'added' | 'updated' = 'added') => {
    setToast({ intent, mode })
    setTimeout(() => setToast(null), 3000)
  }

  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab)
    if (tab !== 'wishlist') {
      setView({ screen: 'home' })
    }
  }

  const handleProductClick = (productId: string) => {
    setView({ screen: 'product', productId })
  }

  const handleBack = () => {
    setView({ screen: 'home' })
    setActiveTab('home')
  }

  const handleAddToBag = (productId: string, size?: string) => {
    const product = PRODUCTS.find(p => p.id === productId)
    if (!product) return
    addToCart(productId, size ?? product.sizes[0])
    setAddedToBagProduct(productId)
    setTimeout(() => setAddedToBagProduct(null), 3000)
  }

  const handleViewMyPicks = () => {
    setActiveTab('wishlist')
    setView({ screen: 'home' })
  }

  const renderView = () => {
    if (view.screen === 'cart') {
      return (
        <CartPage
          onBack={handleBack}
          onContinueShopping={() => { setView({ screen: 'home' }); setActiveTab('home') }}
        />
      )
    }

    if (view.screen === 'product') {
      const product = PRODUCTS.find(p => p.id === view.productId)
      if (!product) return null
      return (
        <ProductDetailPage
          product={product}
          fromContextual={view.fromContextual}
          onBack={handleBack}
          onAddToBag={(size) => handleAddToBag(product.id, size)}
        />
      )
    }

    // Home / Tab views
    if (activeTab === 'wishlist') {
      return (
        <WishlistPage
          onProductClick={handleProductClick}
          onAddToBag={(productId) => handleAddToBag(productId)}
        />
      )
    }

    // Home / Categories / Search / Profile tabs → show home for demo
    return (
      <HomePage
        onProductClick={handleProductClick}
        onViewMyPicks={handleViewMyPicks}
        onAddToBag={(productId) => handleAddToBag(productId)}
      />
    )
  }

  const showBottomNav = view.screen === 'home'
  const showCart = view.screen !== 'cart'

  return (
    <div className="min-h-screen flex justify-center bg-gray-200">
      {/* Mobile frame */}
      <div className="relative w-full max-w-md min-h-screen bg-gray-50 shadow-2xl overflow-hidden">
        {/* Cart FAB (only on non-cart screens) */}
        {showCart && analytics.cartCount > 0 && view.screen !== 'product' && (
          <button
            onClick={() => setView({ screen: 'cart' })}
            className="fixed top-4 left-1/2 -translate-x-1/2 ml-24 z-40 bg-white rounded-full shadow-lg border border-gray-100 flex items-center gap-1.5 px-3 py-1.5"
          >
            <span className="text-xs font-bold text-pink-600">🛍️ {analytics.cartCount}</span>
          </button>
        )}

        {/* Add to Bag confirmation toast */}
        {addedToBagProduct && (() => {
          const product = PRODUCTS.find(p => p.id === addedToBagProduct)
          return (
            <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 w-72">
              <div className="bg-gray-900 text-white rounded-xl px-4 py-3 shadow-xl">
                <p className="text-xs font-bold text-green-400 mb-1">✓ Added to Bag</p>
                <p className="text-[10px] text-gray-300">{product?.brand} — {product?.name}</p>
                <button
                  onClick={() => setView({ screen: 'cart' })}
                  className="mt-2 w-full text-center text-xs text-pink-400 font-semibold"
                >
                  View Bag →
                </button>
              </div>
            </div>
          )
        })()}

        {/* Main content */}
        <div className="relative">
          {renderView()}
        </div>

        {/* Bottom nav */}
        {showBottomNav && (
          <BottomNavigation
            active={activeTab}
            onTabChange={handleTabChange}
            cartCount={analytics.cartCount}
          />
        )}

        {/* Demo panel */}
        <DemoPanel />

        {/* Global toast */}
        {toast && <Toast intent={toast.intent} mode={toast.mode} />}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <StoreProvider>
      <AppShell />
    </StoreProvider>
  )
}
