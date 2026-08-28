import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'
import type { NextQuestion } from '../../types'

interface ChatMessage {
  id: string
  sender: 'ai' | 'patient'
  text: string
  category?: string | null
  timestamp: string
}

export const InterviewPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentPatient, resetFlow } = usePatientStore()
  const {
    currentSession,
    selectedStream,
    selectedDepartment,
    currentQuestion,
    interviewCompleted,
    fetchNextQuestion,
    submitAnswer,
    completeSession,
    resetSession,
    loading,
    error: sessionError,
  } = useSessionStore()

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [textAnswer, setTextAnswer] = useState('')
  const [selectedOption, setSelectedOption] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const chatEndRef = useRef<HTMLDivElement | null>(null)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const addAIQuestionToHistory = (q: NextQuestion) => {
    if (!q.question || q.completed) return
    setChatHistory((prev) => {
      const lastMsg = prev[prev.length - 1]
      if (lastMsg && lastMsg.sender === 'ai' && lastMsg.text === q.question) {
        return prev
      }
      return [
        ...prev,
        {
          id: `ai-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
          sender: 'ai',
          text: q.question as string,
          category: q.category,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]
    })
  }

  // 1. Initial question load
  useEffect(() => {
    if (!currentPatient) {
      navigate('/patient/mobile')
      return
    }
    if (currentSession?.id) {
      fetchNextQuestion(currentSession.id).then((q) => {
        if (q) addAIQuestionToHistory(q)
      }).catch(() => {
        // error handled in store
      })
    }
  }, [currentPatient, currentSession?.id, navigate, fetchNextQuestion])

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const handleSubmitAnswer = async () => {
    if (!currentSession || !currentQuestion || submitting) return
    setErrorMessage(null)

    const qType = currentQuestion.question_type || 'TEXT'
    let rawVal: string | null
    let normVal: Record<string, unknown> | null

    if (qType === 'YES_NO' || qType === 'SINGLE_CHOICE') {
      if (!selectedOption) {
        setErrorMessage('Please select an option to continue.')
        return
      }
      rawVal = selectedOption
      normVal = { selected: selectedOption }
    } else if (qType === 'NUMBER') {
      if (!textAnswer.trim() || isNaN(Number(textAnswer))) {
        setErrorMessage('Please enter a valid number.')
        return
      }
      rawVal = textAnswer.trim()
      normVal = { value: Number(textAnswer.trim()) }
    } else {
      if (currentQuestion.required && !textAnswer.trim()) {
        setErrorMessage('Please enter an answer to continue.')
        return
      }
      rawVal = textAnswer.trim() || null
      normVal = textAnswer.trim() ? { text: textAnswer.trim() } : null
    }

    // Add patient response to chat history
    const userMsgText = rawVal || 'No response provided'
    setChatHistory((prev) => [
      ...prev,
      {
        id: `pat-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
        sender: 'patient',
        text: userMsgText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ])

    setSubmitting(true)
    try {
      await submitAnswer(currentSession.id, {
        patient_id: currentPatient?.id,
        question_id: currentQuestion.question_id,
        raw_answer: rawVal,
        normalized_answer: normVal,
        answer_type: qType,
        source: 'TOUCH',
      })

      // Reset local inputs
      setTextAnswer('')
      setSelectedOption(null)

      // Fetch next question and add to chat
      const nextQ = await fetchNextQuestion(currentSession.id)
      if (nextQ && !nextQ.completed) {
        addAIQuestionToHistory(nextQ)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit answer'
      setErrorMessage(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCompleteIntake = async () => {
    if (!currentSession) return
    setSubmitting(true)
    try {
      await completeSession(currentSession.id)
      resetSession()
      resetFlow()
      navigate('/')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to complete session'
      setErrorMessage(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const quickSuggestions = [
    'Severe headache & fever',
    'Stomach pain for 2 days',
    'Dry cough & sore throat',
    'Body ache and weakness',
  ]

  const severityScale = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  const totalQ = currentQuestion?.total_questions || 5
  const completedCount = currentQuestion?.completed_questions || 0
  const progressPercent = Math.min(100, Math.round((completedCount / totalQ) * 100))

  const isCompleted = interviewCompleted || currentQuestion?.completed
  const qType = currentQuestion?.question_type || 'TEXT'

  return (
    <Container className="py-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-block rounded-full bg-blue-100 px-3 py-0.5 text-xs font-bold uppercase tracking-wider text-blue-800">
              Step 7: AI Clinical Intake
            </span>
            <span className="text-xs text-slate-500 font-medium">
              {selectedStream?.name || 'Modern Medicine'} &bull; {selectedDepartment?.name || 'General Medicine'}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">Clinical Consultation Dialogue</h2>
        </div>
        <div className="text-right w-full sm:w-auto">
          <div className="text-xs text-slate-500 font-medium">Patient</div>
          <div className="font-bold text-slate-900 font-mono text-sm">
            {currentPatient?.full_name} ({currentPatient?.patient_code})
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-5 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex items-center justify-between text-xs font-bold text-slate-600 mb-1.5">
          <span>INTERVIEW PROGRESS</span>
          <span>{completedCount} of {totalQ} answered ({progressPercent}%)</span>
        </div>
        <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {(errorMessage || sessionError) && (
        <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {errorMessage || sessionError}
        </div>
      )}

      {/* CHAT HISTORY — questions and answers only */}
      <div className="rounded-2xl border border-slate-200 bg-slate-50/60 p-4 sm:p-6 mb-5 min-h-[240px] max-h-[400px] overflow-y-auto space-y-4 shadow-inner">
        {chatHistory.length === 0 && (
          <div className="flex items-center justify-center h-32 text-slate-400 text-sm">
            Loading first question...
          </div>
        )}
        {chatHistory.map((msg) => {
          const isAI = msg.sender === 'ai'
          return (
            <div
              key={msg.id}
              className={`flex items-end gap-3 ${isAI ? 'justify-start' : 'justify-end'}`}
            >
              {isAI && (
                <div className="h-9 w-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-base shadow-sm shrink-0 mb-0.5">
                  🩺
                </div>
              )}
              <div
                className={`rounded-2xl px-4 py-3 max-w-[82%] shadow-xs ${
                  isAI
                    ? 'bg-white border border-slate-200 text-slate-900 rounded-bl-sm'
                    : 'bg-blue-600 text-white shadow-md rounded-br-sm'
                }`}
              >
                {isAI && msg.category && (
                  <span className="inline-block text-[10px] font-extrabold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md mb-1.5">
                    {msg.category.replace(/_/g, ' ')}
                  </span>
                )}
                <div className="text-base font-semibold leading-relaxed">{msg.text}</div>
                <div className={`text-[10px] mt-1 ${isAI ? 'text-slate-400 text-right' : 'text-blue-200 text-right'}`}>
                  {msg.timestamp}
                </div>
              </div>
              {!isAI && (
                <div className="h-9 w-9 rounded-full bg-slate-700 text-white flex items-center justify-center text-sm shadow-sm shrink-0 mb-0.5">
                  👤
                </div>
              )}
            </div>
          )
        })}
        <div ref={chatEndRef} />
      </div>

      {/* ANSWER INPUT — only shown when not completed */}
      {isCompleted ? (
        <div className="rounded-2xl border border-emerald-300 bg-emerald-50 p-6 shadow-sm text-center">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 font-bold text-2xl mb-3">
            ✓
          </div>
          <h2 className="text-2xl font-black text-emerald-900">Intake Completed Successfully!</h2>
          <p className="mt-1.5 text-sm text-emerald-800 max-w-md mx-auto">
            All clinical questions have been answered. Responses saved to your patient chart.
          </p>
          <div className="mt-6 flex justify-center">
            <button
              onClick={handleCompleteIntake}
              disabled={submitting}
              className="rounded-xl bg-emerald-700 px-8 py-4 text-base font-bold text-white shadow-md hover:bg-emerald-600 transition cursor-pointer"
            >
              Finish Intake & Return to Home →
            </button>
          </div>
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          {/* INPUT: YES_NO */}
          {qType === 'YES_NO' && (
            <div className="grid grid-cols-3 gap-3 mb-4">
              {[
                { label: 'YES', color: 'emerald' },
                { label: 'NO', color: 'rose' },
                { label: 'NOT SURE', color: 'slate' },
              ].map((opt) => {
                const isSelected = selectedOption === opt.label
                return (
                  <button
                    key={opt.label}
                    type="button"
                    onClick={() => setSelectedOption(opt.label)}
                    className={`py-4 rounded-xl border-2 font-bold text-base transition-all cursor-pointer ${
                      isSelected
                        ? opt.color === 'emerald'
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-md'
                          : opt.color === 'rose'
                          ? 'border-rose-600 bg-rose-50 text-rose-900 shadow-md'
                          : 'border-slate-800 bg-slate-100 text-slate-900 shadow-md'
                        : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    {opt.label}
                  </button>
                )
              })}
            </div>
          )}

          {/* INPUT: SINGLE_CHOICE */}
          {qType === 'SINGLE_CHOICE' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-4">
              {(Array.isArray(currentQuestion?.options)
                ? currentQuestion.options
                : ['Option A', 'Option B']
              ).map((optStr: string) => {
                const isSelected = selectedOption === optStr
                return (
                  <button
                    key={optStr}
                    type="button"
                    onClick={() => setSelectedOption(optStr)}
                    className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all text-left cursor-pointer ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50 text-blue-900 font-bold shadow-md'
                        : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-800 font-medium'
                    }`}
                  >
                    <span>{optStr}</span>
                    <span className={`h-5 w-5 rounded-full border flex items-center justify-center text-xs shrink-0 ${isSelected ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-300 text-transparent'}`}>
                      ✓
                    </span>
                  </button>
                )
              })}
            </div>
          )}

          {/* INPUT: NUMBER */}
          {qType === 'NUMBER' && (
            <div className="space-y-3 mb-4">
              <input
                type="number"
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                placeholder="Enter a number..."
                className="w-full rounded-xl border-2 border-slate-300 px-4 py-3 text-xl font-mono font-bold text-slate-900 focus:border-blue-600 focus:outline-hidden"
              />
              <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5">
                {severityScale.map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setTextAnswer(val.toString())}
                    className={`py-2.5 rounded-lg border-2 font-bold text-xs transition cursor-pointer ${
                      textAnswer === val.toString()
                        ? 'border-blue-600 bg-blue-600 text-white'
                        : 'border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800'
                    }`}
                  >
                    {val}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* INPUT: TEXT / VOICE */}
          {(qType === 'TEXT' || qType === 'VOICE' || (qType !== 'YES_NO' && qType !== 'SINGLE_CHOICE' && qType !== 'NUMBER')) && (
            <div className="space-y-3 mb-4">
              <textarea
                rows={3}
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                placeholder="Type your response here..."
                className="w-full rounded-xl border-2 border-slate-300 p-4 text-base text-slate-900 focus:border-blue-600 focus:outline-hidden leading-relaxed"
              />
              <div className="flex flex-wrap gap-1.5 items-center">
                <span className="text-[11px] font-bold text-slate-400 mr-1">Quick:</span>
                {quickSuggestions.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => setTextAnswer((prev) => (prev ? `${prev}, ${chip}` : chip))}
                    className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100 transition cursor-pointer"
                  >
                    + {chip}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleSubmitAnswer}
            disabled={submitting || loading}
            className="w-full rounded-xl bg-blue-600 py-3.5 text-base font-bold text-white shadow-md hover:bg-blue-500 transition disabled:opacity-50 cursor-pointer"
          >
            {submitting ? 'Submitting...' : 'Submit & Continue →'}
          </button>
        </div>
      )}
    </Container>
  )
}

export default InterviewPage
