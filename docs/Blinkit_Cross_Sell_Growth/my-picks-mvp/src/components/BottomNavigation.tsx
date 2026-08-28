import React from 'react'
import { Home, Grid, Search, Heart, User } from 'lucide-react'

type Tab = 'home' | 'categories' | 'search' | 'wishlist' | 'profile'

interface Props {
  active: Tab
  onTabChange: (tab: Tab) => void
  cartCount: number
}

const tabs = [
  { id: 'home' as Tab, icon: Home, label: 'Home' },
  { id: 'categories' as Tab, icon: Grid, label: 'Categories' },
  { id: 'search' as Tab, icon: Search, label: 'Search' },
  { id: 'wishlist' as Tab, icon: Heart, label: 'Wishlist' },
  { id: 'profile' as Tab, icon: User, label: 'Profile' },
]

export default function BottomNavigation({ active, onTabChange, cartCount }: Props) {
  return (
    <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-100 z-40">
      <div className="flex items-center justify-around py-2 pb-safe">
        {tabs.map(({ id, icon: Icon, label }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              className={`flex flex-col items-center gap-0.5 px-4 py-1 min-w-[44px] transition-colors ${
                isActive ? 'text-pink-600' : 'text-gray-400'
              }`}
            >
              <div className="relative">
                <Icon size={22} strokeWidth={isActive ? 2 : 1.5} fill={isActive && id === 'wishlist' ? '#db2777' : 'none'} />
              </div>
              <span className={`text-[10px] font-medium ${isActive ? 'text-pink-600' : 'text-gray-400'}`}>{label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}

export type { Tab }
