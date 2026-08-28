import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { useSessionStore } from '../../stores'

export const LanguagePage: React.FC = () => {
  const navigate = useNavigate()
  const { availableLanguages, fetchLanguages, setLanguage } = useSessionStore()

  useEffect(() => {
    fetchLanguages()
  }, [fetchLanguages])

  const handleSelectLanguage = (code: string) => {
    if (code !== 'en') return // Only English active for now
    setLanguage(code)
    navigate('/patient/mobile')
  }

  return (
    <Container className="py-10 max-w-xl mx-auto">
      <div className="text-center mb-8">
        <span className="inline-block rounded-full bg-blue-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-blue-800 mb-2">
          Step 1: Language Selection
        </span>
        <h1 className="text-3xl font-black tracking-tight text-slate-900">
          Select Your Preferred Language
        </h1>
        <p className="mt-2 text-base text-slate-600">
          Please select your preferred language to proceed with kiosk check-in
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {availableLanguages.length > 0 ? (
          availableLanguages.map((lang) => {
            const isEnglish = lang.code === 'en'

            return (
              <button
                key={lang.code}
                onClick={() => handleSelectLanguage(lang.code)}
                disabled={!isEnglish}
                className={`relative flex flex-col items-center justify-center p-8 rounded-2xl border-2 transition-all text-center shadow-xs ${
                  isEnglish
                    ? 'border-blue-600 bg-blue-50/40 hover:bg-blue-50 hover:shadow-md cursor-pointer ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-slate-50/70 opacity-60 cursor-not-allowed'
                }`}
              >
                <div className="text-4xl mb-3">
                  {lang.code === 'hi' ? '🇮🇳' : '🌐'}
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {lang.name}
                </div>
                <div className="text-sm font-medium text-slate-500 mt-1">
                  {lang.code === 'hi' ? 'Hindi' : 'English (Default)'}
                </div>

                {isEnglish ? (
                  <div className="mt-4 inline-flex items-center rounded-full bg-blue-600 px-4 py-1.5 text-xs font-bold text-white shadow-xs">
                    Continue in English →
                  </div>
                ) : (
                  <div className="mt-4 inline-flex items-center rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-600">
                    Coming Soon (Disabled)
                  </div>
                )}
              </button>
            )
          })
        ) : (
          <div className="col-span-2 text-center py-8 text-slate-400">
            Loading supported languages...
          </div>
        )}
      </div>
    </Container>
  )
}

export default LanguagePage
