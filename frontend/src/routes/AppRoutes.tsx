import { createBrowserRouter } from 'react-router-dom'

import { RootLayout } from '../layouts/RootLayout'
import { HomePage } from '../pages/HomePage'
import { LoginPage } from '../pages/LoginPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { SystemStatusPage } from '../pages/SystemStatusPage'
import { MobilePage } from '../pages/patient/MobilePage'
import { RegisterPage } from '../pages/patient/RegisterPage'
import { FacePage } from '../pages/patient/FacePage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'system', element: <SystemStatusPage /> },
      // Phase 3 Patient Identity routes
      { path: 'patient/mobile', element: <MobilePage /> },
      { path: 'patient/register', element: <RegisterPage /> },
      { path: 'patient/face', element: <FacePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
