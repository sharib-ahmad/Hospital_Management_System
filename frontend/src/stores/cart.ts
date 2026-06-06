import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useNotificationStore } from './notification'

interface CartItem {
  medicine: any
  quantity: number
}

export const useCartStore = defineStore('cart', () => {
  const notification = useNotificationStore()

  const items = ref<CartItem[]>(
    JSON.parse(localStorage.getItem('medistore_cart') || '[]')
  )

  const cartCount = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const cartTotal = computed(() => {
    return items.value.reduce((sum, item) => sum + item.medicine.price * item.quantity, 0)
  })

  function saveCart() {
    localStorage.setItem('medistore_cart', JSON.stringify(items.value))
  }

  function addToCart(medicine: any) {
    if (medicine.stock <= 0) {
      notification.error('Medicine is currently out of stock')
      return
    }
    const existing = items.value.find((item) => item.medicine.id === medicine.id)
    if (existing) {
      if (existing.quantity >= medicine.stock) {
        notification.error(`Cannot add more. Only ${medicine.stock} units in stock.`)
        return
      }
      existing.quantity++
    } else {
      items.value.push({ medicine, quantity: 1 })
    }
    saveCart()
    notification.success(`${medicine.name} added to basket`)
  }

  function updateQuantity(medicineId: string, quantity: number, maxStock: number) {
    const existing = items.value.find((item) => item.medicine.id === medicineId)
    if (existing) {
      if (quantity > maxStock) {
        notification.error(`Only ${maxStock} units available in stock.`)
        existing.quantity = maxStock
        saveCart()
        return
      }
      if (quantity <= 0) {
        items.value = items.value.filter((item) => item.medicine.id !== medicineId)
        notification.success('Item removed from basket')
      } else {
        existing.quantity = quantity
      }
      saveCart()
    }
  }

  function removeFromCart(medicineId: string, name: string) {
    items.value = items.value.filter((item) => item.medicine.id !== medicineId)
    saveCart()
    notification.success(`${name} removed from basket`)
  }

  function clearCart() {
    items.value = []
    saveCart()
  }

  return {
    items,
    cartCount,
    cartTotal,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
  }
})
