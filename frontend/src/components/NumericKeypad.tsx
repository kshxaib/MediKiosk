import React from 'react'
import { cn } from '../utils/cn'

interface NumericKeypadProps {
  /** Current digit string. Used only for enabling/disabling keys. */
  value: string
  /**
   * Called with the tapped digit. The PARENT must apply it with a functional
   * state update (`setX(prev => prev + digit)`), never by computing from the
   * `value` prop — otherwise several taps landing in one render frame all read
   * the same stale value and only the last digit survives. A patient tapping
   * quickly on a kiosk hits this easily.
   */
  onAppend: (digit: string) => void
  onBackspace: () => void
  onClear: () => void
  /** Maximum number of digits the patient may enter. */
  maxLength: number
  disabled?: boolean
  className?: string
  /** Label on the clear key. */
  clearLabel?: string
}

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

/**
 * Large on-screen numeric keypad for the MediKiosk touchscreen.
 *
 * The kiosk has no physical keyboard, so every numeric entry point (mobile
 * number, numeric interview answers) uses this. Keys are sized for finger taps,
 * give an :active press state rather than relying on :hover, and set
 * touch-manipulation to remove the mobile tap delay.
 */
export const NumericKeypad: React.FC<NumericKeypadProps> = ({
  value,
  onAppend,
  onBackspace,
  onClear,
  maxLength,
  disabled = false,
  className,
  clearLabel = 'Clear',
}) => {
  const atLimit = value.length >= maxLength
  const isEmpty = value.length === 0

  const keyClass = cn(
    'flex items-center justify-center rounded-2xl border-2 border-slate-200 bg-white',
    'text-3xl font-bold text-slate-900 shadow-xs select-none touch-manipulation',
    'h-18 transition active:scale-95 active:bg-blue-50 active:border-blue-500',
    'disabled:opacity-40 disabled:active:scale-100 cursor-pointer',
  )

  return (
    <div className={cn('grid grid-cols-3 gap-3', className)}>
      {KEYS.map((digit) => (
        <button
          key={digit}
          type="button"
          aria-label={`Digit ${digit}`}
          disabled={disabled || atLimit}
          onClick={() => onAppend(digit)}
          className={keyClass}
        >
          {digit}
        </button>
      ))}

      <button
        type="button"
        aria-label={clearLabel}
        disabled={disabled || isEmpty}
        onClick={onClear}
        className={cn(
          keyClass,
          'text-base font-extrabold uppercase tracking-wider text-slate-600',
        )}
      >
        {clearLabel}
      </button>

      <button
        type="button"
        aria-label="Digit 0"
        disabled={disabled || atLimit}
        onClick={() => onAppend('0')}
        className={keyClass}
      >
        0
      </button>

      <button
        type="button"
        aria-label="Backspace"
        disabled={disabled || isEmpty}
        onClick={onBackspace}
        className={cn(keyClass, 'text-3xl text-slate-600')}
      >
        ⌫
      </button>
    </div>
  )
}

export default NumericKeypad
