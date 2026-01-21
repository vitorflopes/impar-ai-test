import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  /**
   * Add a notification
   * @param {Object} notification
   * @param {string} notification.message - The message to display
   * @param {'success' | 'error' | 'info' | 'warning'} [notification.type='info'] - Type of notification
   * @param {number} [notification.duration=3000] - Duration in ms
   */
  function addNotification({ message, type = 'info', duration = 3000 }) {
    const id = Date.now() + Math.random()
    notifications.value.push({
      id,
      message,
      type,
      duration
    })

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
  }

  function removeNotification(id) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return {
    notifications,
    addNotification,
    removeNotification
  }
})
