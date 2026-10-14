import { create } from 'zustand'

interface CartState {
  items: string[]
  add: (id: string) => void
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  add: (id) => set((s) => ({ items: [...s.items, id] })),
}))
