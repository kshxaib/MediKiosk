import React, { useMemo, useState } from 'react'
import type { NextQuestion } from '../types'
import { cn } from '../utils/cn'
import { NumericKeypad } from './NumericKeypad'

export interface SubmittedAnswer {
  raw: string
  normalized: Record<string, unknown>
}

interface QuestionInputProps {
  question: NextQuestion
  /** True while the answer is in flight or the AI is choosing the next question. */
  busy: boolean
  onSubmit: (answer: SubmittedAnswer) => void
  onDirty?: () => void
}

/** Values the kiosk accepts for a YES_NO question when the backend sends none. */
const YES_NO_FALLBACK = ['YES', 'NO']

/** Largest numeric range still rendered as a one-tap grid rather than a keypad. */
const MAX_TAP_GRID_SPAN = 12

function toOptionList(options: NextQuestion['options']): string[] {
  if (Array.isArray(options)) {
    return options.map((o) => String(o)).filter((o) => o.trim().length > 0)
  }
  return []
}

function numericBounds(question: NextQuestion): { min?: number; max?: number } {
  const rules = question.validation_rules
  if (!rules) return {}
  const min = typeof rules.min === 'number' ? rules.min : undefined
  const max = typeof rules.max === 'number' ? rules.max : undefined
  return { min, max }
}

/**
 * Renders the correct touchscreen control for ONE interview question.
 *
 * The control is chosen from the backend's question_type, and every option list
 * comes from the backend — nothing about the clinical questionnaire is hard-coded
 * here. Supported types: TEXT, NUMBER, YES_NO, SINGLE_CHOICE. Anything else falls
 * back to the text control so an unknown type can never block the interview.
 *
 * This component owns its own draft state. InterviewPage remounts it (via `key`)
 * whenever the question changes, which is what guarantees the control switches
 * cleanly and no stale draft carries over between questions.
 */
export const QuestionInput: React.FC<QuestionInputProps> = ({
  question,
  busy,
  onSubmit,
  onDirty,
}) => {
  const type = (question.question_type || 'TEXT').toUpperCase()
  const [text, setText] = useState('')
  const [digits, setDigits] = useState('')
  const [selected, setSelected] = useState<string | null>(null)

  const options = useMemo(() => toOptionList(question.options), [question.options])
  const { min, max } = numericBounds(question)
  const maxDigits = String(max ?? 999).length

  // A short bounded range (severity 1-10) is far easier to tap as a grid than to
  // type. A wide range (sleep hours 0-24) gets the keypad instead.
  const tapValues = useMemo(() => {
    if (type !== 'NUMBER') return null
    if (min === undefined || max === undefined) return null
    if (max - min < 1 || max - min + 1 > MAX_TAP_GRID_SPAN) return null
    return Array.from({ length: max - min + 1 }, (_, i) => min + i)
  }, [type, min, max])

  const touched = () => onDirty?.()

  const numberValue = digits.length ? Number(digits) : null
  const numberInRange =
    numberValue !== null &&
    Number.isFinite(numberValue) &&
    (min === undefined || numberValue >= min) &&
    (max === undefined || numberValue <= max)

  const canSubmit = (() => {
    if (busy) return false
    if (type === 'YES_NO' || type === 'SINGLE_CHOICE') return Boolean(selected)
    if (type === 'NUMBER') return numberInRange
    return text.trim().length > 0
  })()

  const submit = () => {
    if (!canSubmit) return
    if (type === 'YES_NO' || type === 'SINGLE_CHOICE') {
      onSubmit({ raw: selected as string, normalized: { selected } })
      return
    }
    if (type === 'NUMBER') {
      onSubmit({ raw: String(numberValue), normalized: { value: numberValue } })
      return
    }
    const trimmed = text.trim()
    onSubmit({ raw: trimmed, normalized: { text: trimmed } })
  }

  // ── Shared button styles (touch-first: :active feedback, no hover reliance) ──
  const choiceBase =
    'w-full touch-manipulation select-none rounded-2xl border-2 p-5 text-left transition ' +
    'active:scale-[0.98] disabled:opacity-40 cursor-pointer'
  const choiceIdle = 'border-slate-200 bg-white text-slate-800'
  const choiceOn = 'border-blue-600 bg-blue-50 text-blue-900 shadow-md ring-4 ring-blue-500/15'

  const renderControl = () => {
    // ── YES_NO ────────────────────────────────────────────────────────────
    if (type === 'YES_NO') {
      const yesNoOptions = options.length ? options : YES_NO_FALLBACK
      const tone = (opt: string) => {
        const u = opt.trim().toUpperCase()
        if (u === 'YES') return { on: 'border-emerald-600 bg-emerald-50 text-emerald-900 ring-emerald-500/20' }
        if (u === 'NO') return { on: 'border-rose-600 bg-rose-50 text-rose-900 ring-rose-500/20' }
        return { on: 'border-slate-800 bg-slate-100 text-slate-900 ring-slate-500/20' }
      }
      return (
        <div
          className={cn(
            'grid gap-3 mb-5',
            yesNoOptions.length >= 3 ? 'grid-cols-1 sm:grid-cols-3' : 'grid-cols-2',
          )}
        >
          {yesNoOptions.map((opt) => {
            const on = selected === opt
            return (
              <button
                key={opt}
                type="button"
                aria-pressed={on}
                disabled={busy}
                onClick={() => {
                  setSelected(opt)
                  touched()
                }}
                className={cn(
                  'touch-manipulation select-none rounded-2xl border-2 py-8 text-2xl font-extrabold',
                  'transition active:scale-[0.98] disabled:opacity-40 cursor-pointer',
                  on
                    ? cn('shadow-md ring-4', tone(opt).on)
                    : 'border-slate-200 bg-white text-slate-700',
                )}
              >
                {opt}
              </button>
            )
          })}
        </div>
      )
    }

    // ── SINGLE_CHOICE ─────────────────────────────────────────────────────
    if (type === 'SINGLE_CHOICE') {
      if (!options.length) {
        return (
          <div className="mb-5 rounded-2xl border-2 border-amber-200 bg-amber-50 p-5 text-base font-semibold text-amber-900">
            No answer choices are available for this question. Please tap Retry.
          </div>
        )
      }
      return (
        <div className="grid grid-cols-1 gap-3 mb-5">
          {options.map((opt) => {
            const on = selected === opt
            return (
              <button
                key={opt}
                type="button"
                aria-pressed={on}
                disabled={busy}
                onClick={() => {
                  setSelected(opt)
                  touched()
                }}
                className={cn(
                  choiceBase,
                  'flex items-center justify-between gap-4',
                  on ? choiceOn : choiceIdle,
                )}
              >
                <span className="text-xl font-bold leading-snug">{opt}</span>
                <span
                  className={cn(
                    'flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 text-lg font-black',
                    on
                      ? 'border-blue-600 bg-blue-600 text-white'
                      : 'border-slate-300 text-transparent',
                  )}
                >
                  ✓
                </span>
              </button>
            )
          })}
        </div>
      )
    }

    // ── NUMBER ────────────────────────────────────────────────────────────
    if (type === 'NUMBER') {
      const display = digits.length ? digits : '—'
      return (
        <div className="mb-5 space-y-4">
          <div className="rounded-2xl border-2 border-slate-200 bg-slate-50 py-6 text-center">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500">
              Your answer
            </div>
            <div
              className={cn(
                'mt-1 font-mono text-6xl font-black tabular-nums',
                digits.length ? 'text-slate-900' : 'text-slate-300',
              )}
            >
              {display}
            </div>
            {(min !== undefined || max !== undefined) && (
              <div className="mt-1 text-sm font-semibold text-slate-500">
                Choose a number between {min ?? 0} and {max ?? '—'}
              </div>
            )}
          </div>

          {tapValues ? (
            <div className="grid grid-cols-5 gap-3">
              {tapValues.map((val) => {
                const on = digits === String(val)
                return (
                  <button
                    key={val}
                    type="button"
                    aria-pressed={on}
                    disabled={busy}
                    onClick={() => {
                      setDigits(String(val))
                      touched()
                    }}
                    className={cn(
                      'touch-manipulation select-none rounded-2xl border-2 py-6 text-2xl font-extrabold',
                      'transition active:scale-95 disabled:opacity-40 cursor-pointer',
                      on
                        ? 'border-blue-600 bg-blue-600 text-white shadow-md'
                        : 'border-slate-200 bg-white text-slate-800',
                    )}
                  >
                    {val}
                  </button>
                )
              })}
            </div>
          ) : (
            <NumericKeypad
              value={digits}
              onAppend={(d) => {
                setDigits((prev) => (prev.length >= maxDigits ? prev : prev + d))
                touched()
              }}
              onBackspace={() => {
                setDigits((prev) => prev.slice(0, -1))
                touched()
              }}
              onClear={() => {
                setDigits('')
                touched()
              }}
              maxLength={maxDigits}
              disabled={busy}
            />
          )}

          {digits.length > 0 && !numberInRange && (
            <div className="rounded-xl border-2 border-amber-300 bg-amber-50 px-4 py-3 text-base font-bold text-amber-900">
              Please choose a number between {min ?? 0} and {max ?? '—'}.
            </div>
          )}
        </div>
      )
    }

    // ── TEXT (and any unrecognised type) ──────────────────────────────────
    return (
      <div className="mb-5">
        <textarea
          rows={4}
          disabled={busy}
          value={text}
          onChange={(e) => {
            setText(e.target.value)
            touched()
          }}
          placeholder="Tap here and describe how you are feeling..."
          className={cn(
            'w-full rounded-2xl border-2 border-slate-300 p-5 text-xl leading-relaxed text-slate-900',
            'focus:border-blue-600 focus:outline-hidden disabled:bg-slate-100',
          )}
        />
        <p className="mt-2 px-1 text-sm font-medium text-slate-500">
          Describe it in your own words — you can mention how long you have had it
          and how bad it feels.
        </p>
      </div>
    )
  }

  return (
    <div>
      {renderControl()}
      <button
        type="button"
        onClick={submit}
        disabled={!canSubmit}
        className={cn(
          'flex w-full touch-manipulation items-center justify-center gap-3 rounded-2xl',
          'bg-blue-600 py-6 text-xl font-bold text-white shadow-md transition',
          'active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer',
        )}
      >
        {busy ? (
          <>
            <span className="inline-block h-6 w-6 animate-spin rounded-full border-3 border-white border-t-transparent" />
            <span>Processing your answer...</span>
          </>
        ) : (
          <span>Submit Answer &amp; Continue →</span>
        )}
      </button>
    </div>
  )
}

export default QuestionInput
