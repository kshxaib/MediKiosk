import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container } from '../../components/Container'
import { usePatientStore, useSessionStore } from '../../stores'
import type { Department } from '../../types'

export const DepartmentPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentPatient } = usePatientStore()
  const {
    currentSession,
    selectedStream,
    availableDepartments,
    fetchDepartments,
    setDepartment,
    updateSession,
    loading,
    error: sessionError,
  } = useSessionStore()

  const [submittingDeptId, setSubmittingDeptId] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!currentPatient) {
      navigate('/patient/mobile')
      return
    }
    fetchDepartments(selectedStream?.code)
  }, [currentPatient, selectedStream, navigate, fetchDepartments])

  const handleSelectDepartment = async (dept: Department) => {
    if (!currentSession || submittingDeptId) return
    setErrorMessage(null)
    setSubmittingDeptId(dept.id)

    try {
      setDepartment(dept)
      await updateSession(currentSession.id, {
        department_id: dept.id,
      })
      navigate('/patient/interview')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to select department'
      setErrorMessage(msg)
    } finally {
      setSubmittingDeptId(null)
    }
  }

  const deptIcons: Record<string, string> = {
    GEN_MED: '🩺',
    CARDIO: '🫀',
    NEURO: '🧠',
    ORTHO: '🦴',
    DERMA: '🔬',
    AYURVEDA: '🌿',
  }

  return (
    <Container className="py-8 max-w-3xl mx-auto">
      <div className="text-center mb-6">
        <span className="inline-block rounded-full bg-blue-100 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-blue-800 mb-2">
          Step 6: Clinical Department
        </span>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900">
          Select Department
        </h1>
        {selectedStream && (
          <p className="mt-1 text-sm text-slate-500">
            Selected Stream: <span className="font-semibold text-blue-700">{selectedStream.name}</span>
          </p>
        )}
      </div>

      {(errorMessage || sessionError) && (
        <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 flex items-center justify-between">
          <span>{errorMessage || sessionError}</span>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-red-500 hover:text-red-700 text-xs font-bold ml-2 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {loading && availableDepartments.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-48 space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <div className="text-sm font-bold text-slate-500">Loading departments...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {availableDepartments.map((dept) => {
            const icon = deptIcons[dept.code] || '🩺'
            const isSelected = submittingDeptId === dept.id

            return (
              <button
                key={dept.id}
                onClick={() => handleSelectDepartment(dept)}
                disabled={Boolean(submittingDeptId)}
                className={`flex flex-col items-start p-5 rounded-2xl border-2 transition text-left cursor-pointer group relative ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/50 shadow-md ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-white hover:border-blue-500 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-2">
                  <span className="text-3xl">{icon}</span>
                  <span className="font-mono text-xs font-bold text-slate-400 group-hover:text-blue-600">
                    {dept.code}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition">
                  {dept.name}
                </h3>
                <p className="mt-1.5 text-xs text-slate-500 line-clamp-2 leading-relaxed">
                  {dept.description || 'Clinical consultation & diagnosis'}
                </p>
                <div className="mt-4 font-bold text-xs text-blue-600 flex items-center gap-1.5 group-hover:translate-x-1 transition-transform">
                  {isSelected ? (
                    <>
                      <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent inline-block" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <span>Choose Department →</span>
                  )}
                </div>
              </button>
            )
          })}
        </div>
      )}
    </Container>
  )
}

export default DepartmentPage
