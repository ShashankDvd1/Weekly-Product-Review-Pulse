import React, { useEffect, useState } from 'react'
import { Intent } from '../types'

import { useAppStore } from '../state/StoreContext'

interface Props {
  intent: Intent
  mode?: 'added' | 'updated'
}

export default function Toast({ intent, mode = 'added' }: Props) {
  const { categories } = useAppStore()
  const [visible, setVisible] = useState(true)
  const meta = categories.find(c => c.id === intent) || { emoji: '✨', label: intent }

  useEffect(() => {
    const t = setTimeout(() => setVisible(false), 2800)
    return () => clearTimeout(t)
  }, [])

  if (!visible) return null

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-bottom-4 duration-300">
      <div className="bg-gray-900 text-white rounded-xl px-4 py-3 shadow-xl flex items-center gap-3 min-w-48">
        <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-xs font-bold flex-shrink-0">✓</div>
        <div>
          <p className="text-xs font-semibold leading-tight">
            {mode === 'added' ? 'Added to My Picks' : 'My Pick updated'}
          </p>
          <p className="text-xs text-gray-300 mt-0.5">{meta.emoji} {meta.label}</p>
        </div>
      </div>
    </div>
  )
}
