import { createBrowserRouter } from 'react-router-dom'

import { RootLayout } from '../layouts/RootLayout'
import { HomePage } from '../pages/HomePage'
import { LoginPage } from '../pages/LoginPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { SystemStatusPage } from '../pages/SystemStatusPage'
import { ConsentPage } from '../pages/patient/ConsentPage'
import { DepartmentPage } from '../pages/patient/DepartmentPage'
import { FacePage } from '../pages/patient/FacePage'
import { InterviewPage } from '../pages/patient/InterviewPage'
import { InterviewReadyPage } from '../pages/patient/InterviewReadyPage'
import { LanguagePage } from '../pages/patient/LanguagePage'
import { MobilePage } from '../pages/patient/MobilePage'
import { RegisterPage } from '../pages/patient/RegisterPage'
import { StreamPage } from '../pages/patient/StreamPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'system', element: <SystemStatusPage /> },
      // Phase 3, 4, 5A Patient Intake Flow
      { path: 'patient/language', element: <LanguagePage /> },
      { path: 'patient/mobile', element: <MobilePage /> },
      { path: 'patient/register', element: <RegisterPage /> },
      { path: 'patient/face', element: <FacePage /> },
      { path: 'patient/consent', element: <ConsentPage /> },
      { path: 'patient/stream', element: <StreamPage /> },
      { path: 'patient/department', element: <DepartmentPage /> },
      { path: 'patient/ready', element: <InterviewReadyPage /> },
      { path: 'patient/interview', element: <InterviewPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
