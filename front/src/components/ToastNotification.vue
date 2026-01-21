<script setup>
import { useNotificationStore } from '../stores/notification'
import { storeToRefs } from 'pinia'

const store = useNotificationStore()
const { notifications } = storeToRefs(store)
const { removeNotification } = store
</script>

<template>
  <div class="notification-container">
    <TransitionGroup name="toast">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="toast"
        :class="notification.type"
        @click="removeNotification(notification.id)"
      >
        <div class="content">
            <span v-if="notification.type === 'error'" class="icon">✕</span>
            <span v-else-if="notification.type === 'success'" class="icon">✓</span>
            <span v-else class="icon">ℹ</span>
            <p>{{ notification.message }}</p>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 9999;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  min-width: 300px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(20, 20, 20, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 0.95rem;
}

.content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.9em;
  flex-shrink: 0;
}

.toast.error .icon {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.toast.error {
  border-left: 3px solid #ef4444;
}

.toast.success .icon {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.toast.success {
  border-left: 3px solid #10b981;
}

.toast.warning .icon {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.toast.warning {
  border-left: 3px solid #f59e0b;
}

.toast.info .icon {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.toast.info {
  border-left: 3px solid #3b82f6;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
