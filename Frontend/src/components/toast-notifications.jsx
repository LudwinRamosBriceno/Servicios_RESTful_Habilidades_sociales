/* eslint-disable react-refresh/only-export-components */
import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, Info, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import './toast-notifications.css'

function ToastItem({ toast, onDismiss }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 4000)
    return () => clearTimeout(timer)
  }, [toast.id, onDismiss])

  return (
    <div
      className={cn(
        'toast-item',
        toast.className || (
          toast.type === 'success'
            ? 'toast-item-success'
            : toast.type === 'error'
            ? 'toast-item-error'
            : 'toast-item-info'
        )
      )}
      role="alert"
      aria-live="polite"
    >
      {toast.type === 'success' ? (
        <CheckCircle className="toast-item-icon" />
      ) : toast.type === 'error' ? (
        <XCircle className="toast-item-icon" />
      ) : (
        <Info className="toast-item-icon" />
      )}
      <span className="toast-item-message">{toast.message}</span>
      <button
        onClick={() => onDismiss(toast.id)}
        className="toast-item-close-button"
        aria-label="Dismiss notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}

export function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="toast-container" aria-label="Notifications">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

// Hook for managing toasts
export function useToasts() {
  const [toasts, setToasts] = useState([])

  const addToast = (type, message, options = {}) => {
    const id = crypto.randomUUID()
    setToasts((prev) => [...prev, { id, type, message, ...options }])
  }

  const dismiss = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  return { toasts, addToast, dismiss }
}
