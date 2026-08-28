import React, { createContext, useContext } from 'react'
import { useStore } from './useStore'
import type { Store } from './useStore'

const StoreContext = createContext<Store | null>(null)

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const store = useStore()
  return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>
}

export function useAppStore(): Store {
  const ctx = useContext(StoreContext)
  if (!ctx) throw new Error('useAppStore must be used inside StoreProvider')
  return ctx
}
