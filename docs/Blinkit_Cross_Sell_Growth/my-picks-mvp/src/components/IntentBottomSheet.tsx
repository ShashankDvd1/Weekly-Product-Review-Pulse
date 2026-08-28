import React, { useState, useCallback } from 'react'
import { useAppStore } from '../state/StoreContext'
import { Intent, INTENT_META } from '../types'

interface Props {
  productId: string
  onClose: () => void
  mode?: 'save' | 'change'
}

export default function IntentBottomSheet({ productId, onClose, mode = 'save' }: Props) {
  const { setIntent, clearIntent, logEvent } = useAppStore()
  const [selected, setSelected] = useState<Intent | null>(null)
  const [closing, setClosing] = useState(false)

  const dismiss = useCallback((chosenIntent?: Intent) => {
    setClosing(true)
    setTimeout(() => {
      if (chosenIntent) {
        setIntent(productId, chosenIntent)
      } else {
        logEvent('INTENT_SKIPPED', productId, null)
      }
      onClose()
    }, 200)
  }, [productId, setIntent, logEvent, onClose])

  const handleSelect = (intent: Intent) => {
    setSelected(intent)
    setTimeout(() => dismiss(intent), 350)
  }

  const intents: Intent[] = ['BUY_SOON', 'WAITING_FOR_PRICE', 'COMPARING', 'JUST_SAVING']

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end" onClick={() => dismiss()}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-xs" />

      {/* Sheet */}
      <div
        className={`relative bg-white rounded-t-2xl px-5 pt-5 pb-8 transition-transform duration-200 ${closing ? 'translate-y-full' : 'translate-y-0'}`}
        onClick={e => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-4" />

        {/* Header */}
        <div className="flex items-center gap-2 mb-1">
          <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center text-xs">✓</div>
          <span className="font-semibold text-sm text-gray-800">
            {mode === 'change' ? 'Change your intent' : 'Saved to Wishlist'}
          </span>
        </div>

        <h2 className="text-lg font-bold text-gray-900 mt-3 mb-1">What are you saving this for?</h2>
        <p className="text-sm text-gray-500 mb-4">Tell us once so we can make your Wishlist more useful.</p>

        {/* Intent Cards */}
        <div className="grid grid-cols-2 gap-2 mb-4">
          {intents.map(intent => {
            const meta = INTENT_META[intent]
            const isSelected = selected === intent
            return (
              <button
                key={intent}
                onClick={() => handleSelect(intent)}
                className={`relative text-left rounded-xl border-2 p-3 transition-all duration-150 active:scale-95 ${
                  isSelected
                    ? 'border-pink-500 bg-pink-50 shadow-sm'
                    : 'border-gray-100 bg-gray-50 hover:border-pink-200'
                }`}
              >
                {isSelected && (
                  <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-pink-500 flex items-center justify-center text-white text-xs">✓</div>
                )}
                <span className="text-xl">{meta.emoji}</span>
                <p className="font-semibold text-sm text-gray-900 mt-1">{meta.label}</p>
                <p className="text-xs text-gray-500 leading-tight mt-0.5">{meta.description}</p>
              </button>
            )
          })}
        </div>

        {/* Skip */}
        <button
          onClick={() => dismiss()}
          className="w-full py-3 text-sm text-gray-500 hover:text-gray-700 font-medium transition-colors"
        >
          Skip for now
        </button>
      </div>
    </div>
  )
}
