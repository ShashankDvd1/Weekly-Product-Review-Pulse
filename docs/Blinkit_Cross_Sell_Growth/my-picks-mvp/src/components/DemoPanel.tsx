import React, { useState } from 'react'
import { BarChart3, RefreshCw, Zap, X, ChevronDown, ChevronUp } from 'lucide-react'
import { useAppStore } from '../state/StoreContext'
import { INTENT_META } from '../types'

export default function DemoPanel() {
  const { analytics, resetDemo, simulatePlus30Days, setAllBuySoon, simDateOffsetDays } = useAppStore()
  const [open, setOpen] = useState(false)
  const [metricsOpen, setMetricsOpen] = useState(false)

  return (
    <>
      {/* Trigger */}
      <button
        onClick={() => setOpen(true)}
        className="fixed top-4 right-4 z-50 bg-gray-900 text-white text-[10px] font-bold px-2.5 py-1.5 rounded-full flex items-center gap-1 shadow-lg opacity-60 hover:opacity-100 transition-opacity"
      >
        <Zap size={10} /> Demo
      </button>

      {/* Panel */}
      {open && (
        <div className="fixed inset-0 z-[60] flex flex-col justify-end">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <div className="relative bg-white rounded-t-2xl px-5 pt-5 pb-8 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Zap size={16} className="text-pink-600" />
                <h2 className="font-black text-gray-900">Demo Controls</h2>
              </div>
              <button onClick={() => setOpen(false)} className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center">
                <X size={14} />
              </button>
            </div>

            {simDateOffsetDays > 0 && (
              <div className="mb-3 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2 text-xs text-amber-700 font-medium">
                🕐 Simulated date: +{simDateOffsetDays} days ahead
              </div>
            )}

            {/* Controls */}
            <div className="space-y-2">
              <button
                onClick={resetDemo}
                className="w-full flex items-center gap-3 bg-gray-50 rounded-xl p-3 text-left hover:bg-gray-100 transition-colors"
              >
                <RefreshCw size={16} className="text-gray-500 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-gray-800">Reset Demo</p>
                  <p className="text-xs text-gray-400">Restore default wishlist & clear cart</p>
                </div>
              </button>

              <button
                onClick={simulatePlus30Days}
                className="w-full flex items-center gap-3 bg-amber-50 rounded-xl p-3 text-left hover:bg-amber-100 transition-colors border border-amber-100"
              >
                <span className="text-base flex-shrink-0">🕐</span>
                <div>
                  <p className="text-sm font-semibold text-amber-800">Simulate +30 Days</p>
                  <p className="text-xs text-amber-600">Advance simulated date to show re-engagement</p>
                </div>
              </button>

              <button
                onClick={setAllBuySoon}
                className="w-full flex items-center gap-3 bg-orange-50 rounded-xl p-3 text-left hover:bg-orange-100 transition-colors border border-orange-100"
              >
                <span className="text-base flex-shrink-0">🔥</span>
                <div>
                  <p className="text-sm font-semibold text-orange-800">Set All to Buy Soon</p>
                  <p className="text-xs text-orange-600">For demonstrating re-entry flow</p>
                </div>
              </button>
            </div>

            {/* Metrics */}
            <div className="mt-4">
              <button
                onClick={() => setMetricsOpen(!metricsOpen)}
                className="w-full flex items-center justify-between bg-blue-50 rounded-xl p-3 border border-blue-100"
              >
                <div className="flex items-center gap-2">
                  <BarChart3 size={16} className="text-blue-600" />
                  <span className="text-sm font-semibold text-blue-800">MY PICKS MVP — Metrics Panel</span>
                </div>
                {metricsOpen ? <ChevronUp size={14} className="text-blue-600" /> : <ChevronDown size={14} className="text-blue-600" />}
              </button>

              {metricsOpen && (
                <div className="mt-2 bg-gray-50 rounded-xl p-3 border border-gray-100">
                  <p className="text-[9px] text-gray-400 uppercase font-bold mb-3 tracking-widest">Demo data — not real Myntra data</p>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { label: 'Wishlist Items', value: analytics.total, color: 'text-gray-900' },
                      { label: 'Intent Capture Rate', value: `${analytics.intentCaptureRate}%`, color: 'text-green-600' },
                      { label: 'Buy Soon Items', value: analytics.buySoon, color: 'text-orange-600' },
                      { label: 'Add to Bag', value: analytics.addToBag, color: 'text-purple-600' },
                      { label: 'Purchases', value: analytics.purchases, color: 'text-pink-600' },
                      { label: 'Wishlist → Purchase', value: analytics.total ? `${Math.round((analytics.purchases / analytics.total) * 100)}%` : '0%', color: 'text-blue-600' },
                    ].map(({ label, value, color }) => (
                      <div key={label} className="bg-white rounded-lg p-2.5 text-center shadow-sm">
                        <p className={`text-lg font-black ${color}`}>{value}</p>
                        <p className="text-[9px] text-gray-400 font-medium leading-tight mt-0.5">{label}</p>
                      </div>
                    ))}
                  </div>

                  {/* Intent Distribution */}
                  <div className="mt-3">
                    <p className="text-[9px] text-gray-400 uppercase font-bold mb-2 tracking-widest">Intent Distribution</p>
                    {(['BUY_SOON', 'WAITING_FOR_PRICE', 'COMPARING', 'JUST_SAVING'] as const).map(intent => {
                      const count = analytics.total > 0
                        ? Math.round((analytics.events.filter(e => e.intent === intent).length / Math.max(analytics.total, 1)) * 100)
                        : 0
                      const meta = INTENT_META[intent]
                      return (
                        <div key={intent} className="flex items-center gap-2 mb-1">
                          <span className="text-xs w-4">{meta.emoji}</span>
                          <span className="text-[10px] text-gray-600 w-24 flex-shrink-0">{meta.label}</span>
                          <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-pink-400 rounded-full" style={{ width: `${count}%` }} />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
