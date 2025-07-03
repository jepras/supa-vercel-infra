import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider } from '@/components/auth-provider'
import { logEnvironmentStatus } from '@/lib/env-validation'
import { getAppTitle } from '@/lib/utils'
import { ReactNode } from 'react'

const inter = Inter({ subsets: ['latin'] })

export async function generateMetadata() {
  const isProd = process.env.NODE_ENV === 'production'
  return {
    title: isProd ? 'prod ai infra' : 'local ai infra',
    description: 'AI-driven sales opportunity detection between sent emails and Pipedrive CRM',
  }
}

// Log environment status on server startup
if (typeof window === 'undefined') {
  logEnvironmentStatus()
}

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
} 