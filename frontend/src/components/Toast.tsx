interface ToastProps {
  message: string
  type: 'success' | 'error'
}

export default function Toast({ message, type }: ToastProps) {
  return (
    <div className={`toast ${type}`}>
      <span>{type === 'success' ? '✓' : '✗'}</span>
      <span style={{ marginLeft: 'var(--space-sm)' }}>{message}</span>
    </div>
  )
}
