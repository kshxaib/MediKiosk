import { createBrowserRouter } from 'react-router-dom'

import { RootLayout } from '../layouts/RootLayout'
import { HomePage } from '../pages/HomePage'
import { LoginPage } from '../pages/LoginPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { SystemStatusPage } from '../pages/SystemStatusPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'system', element: <SystemStatusPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
