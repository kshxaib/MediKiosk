import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { QuestionInput, type SubmittedAnswer } from '../../components/QuestionInput'
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
    loading: sessionLoading,
    error: sessionError,
  } = useSessionStore()

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [isAiThinking, setIsAiThinking] = useState(false)
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
          id: `ai-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
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
      fetchNextQuestion(currentSession.id)
        .then((q) => {
          if (q) addAIQuestionToHistory(q)
        })
        .catch(() => {
          setErrorMessage('Unable to load clinical intake question. Please tap Retry.')
        })
        .finally(() => {
          setInitialLoading(false)
        })
    }
  }, [currentPatient, currentSession?.id, navigate, fetchNextQuestion])

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory, isAiThinking])

  // Validate form state
  const qType = currentQuestion?.question_type || 'TEXT'

  const handleRetry = async () => {
    if (!currentSession) return
    setErrorMessage(null)
    setIsAiThinking(true)
    try {
      const q = await fetchNextQuestion(currentSession.id)
      if (q && !q.completed) {
        addAIQuestionToHistory(q)
      }
    } catch {
      setErrorMessage('Failed to connect. Please tap Retry again.')
    } finally {
      setIsAiThinking(false)
    }
  }

  const handleSubmitAnswer = async (answer: SubmittedAnswer) => {
    if (!currentSession || !currentQuestion || submitting || isAiThinking) return
    setErrorMessage(null)

    // Add patient response to chat history immediately
    setChatHistory((prev) => [
      ...prev,
      {
        id: `pat-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        sender: 'patient',
        text: answer.raw,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ])

    setSubmitting(true)
    setIsAiThinking(true)

    try {
      await submitAnswer(currentSession.id, {
        patient_id: currentPatient?.id,
        question_id: currentQuestion.question_id,
        raw_answer: answer.raw,
        normalized_answer: answer.normalized,
        answer_type: qType,
        source: 'TOUCH',
        // AI-generated follow-ups have no question_id; send the question text so
        // the backend can attribute the answer and not repeat the question.
        ...(currentQuestion.question_id
          ? {}
          : { asked_question_text: currentQuestion.question }),
      })

      // Fetch next adaptive question
      const nextQ = await fetchNextQuestion(currentSession.id)
      if (nextQ && !nextQ.completed) {
        addAIQuestionToHistory(nextQ)
      }
    } catch {
      setErrorMessage('Something went wrong submitting your answer. Please tap Retry.')
    } finally {
      setSubmitting(false)
      setIsAiThinking(false)
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
    } catch {
      setErrorMessage('Failed to complete intake session. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const totalQ = currentQuestion?.total_questions || 5
  const completedCount = currentQuestion?.completed_questions || 0
  const progressPercent = Math.min(100, Math.round((completedCount / totalQ) * 100))
  const isCompleted = interviewCompleted || currentQuestion?.completed

  // Remounting the answer control whenever the question changes is what
  // guarantees the correct control is rendered for each question_type and that
  // no draft from the previous question survives.
  const inputKey = currentQuestion
    ? `${currentQuestion.question_id ?? 'adhoc'}|${currentQuestion.question_type ?? 'TEXT'}|${currentQuestion.question ?? ''}`
    : 'none'

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

      {/* Error Card with Retry Button */}
      {(errorMessage || sessionError) && (
        <div className="mb-4 rounded-xl border border-amber-300 bg-amber-50 p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="font-bold text-amber-900 text-sm">Something went wrong</div>
              <div className="text-xs text-amber-800">{errorMessage || sessionError}</div>
            </div>
          </div>
          <button
            onClick={handleRetry}
            disabled={submitting || isAiThinking}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-sm transition cursor-pointer shrink-0"
          >
            Retry Question ⟳
          </button>
        </div>
      )}

      {/* CHAT HISTORY */}
      <div className="rounded-2xl border border-slate-200 bg-slate-50/60 p-4 sm:p-6 mb-5 min-h-[260px] max-h-[420px] overflow-y-auto space-y-4 shadow-inner">
        {initialLoading && chatHistory.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 space-y-3">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
            <div className="text-sm font-bold text-slate-500">Initializing clinical consultation...</div>
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

        {/* AI Typing Indicator */}
        {isAiThinking && (
          <div className="flex items-end gap-3 justify-start">
            <div className="h-9 w-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-base shadow-sm shrink-0 mb-0.5">
              🩺
            </div>
            <div className="rounded-2xl rounded-bl-sm bg-white border border-slate-200 px-4 py-3 shadow-xs">
              <div className="flex items-center space-x-1.5 py-1">
                <span className="text-xs font-bold text-slate-500 mr-2">Evaluating response</span>
                <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* ANSWER INPUT AREA */}
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
              className="rounded-xl bg-emerald-700 px-8 py-4 text-base font-bold text-white shadow-md hover:bg-emerald-600 transition disabled:opacity-50 cursor-pointer"
            >
              {submitting ? 'Finishing...' : 'Finish Intake & Return to Home →'}
            </button>
          </div>
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          {/*
            The answer control is chosen from the backend question_type and is
            remounted per question via `inputKey`, so switching between
            TEXT / NUMBER / YES_NO / SINGLE_CHOICE always renders the right
            control and never leaves a previous draft behind.
          */}
          {currentQuestion && (
            <QuestionInput
              key={inputKey}
              question={currentQuestion}
              busy={submitting || isAiThinking || sessionLoading}
              onSubmit={handleSubmitAnswer}
              onDirty={() => setErrorMessage(null)}
            />
          )}
        </div>
      )}
    </Container>
  )
}

export default InterviewPage
