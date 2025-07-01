'use client'

import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useState, useEffect } from 'react'
import { useAuth } from '@/components/auth-provider'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [debugInfo, setDebugInfo] = useState('')
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()

  // Redirect if already authenticated
  useEffect(() => {
    if (user && !authLoading) {
      console.log('User already authenticated, redirecting to dashboard')
      router.push('/dashboard')
    }
  }, [user, authLoading, router])

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')
    setDebugInfo('')

    if (!email || !password) {
      setError('Email and password are required')
      setIsLoading(false)
      return
    }

    try {
      if (mode === 'signin') {
        console.log('Attempting to sign in with:', email)
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        
        if (error) {
          console.error('Sign in error:', error)
          setError(error.message)
          setDebugInfo(`Error code: ${error.status}, Message: ${error.message}`)
        } else {
          console.log('Sign in successful:', data)
          setSuccess('Signed in successfully! Redirecting...')
          setDebugInfo(`User ID: ${data.user?.id}, Email: ${data.user?.email}`)
          // The AuthProvider will handle the redirect
        }
      } else {
        console.log('Attempting to sign up with:', email)
        const { data, error } = await supabase.auth.signUp({ email, password })
        
        if (error) {
          console.error('Sign up error:', error)
          setError(error.message)
          setDebugInfo(`Error code: ${error.status}, Message: ${error.message}`)
        } else {
          console.log('Sign up successful:', data)
          setSuccess('Check your email to confirm your account.')
          setDebugInfo(`User ID: ${data.user?.id}, Email confirmed: ${data.user?.email_confirmed_at ? 'Yes' : 'No'}`)
        }
      }
    } catch (err) {
      console.error('Unexpected error:', err)
      setError('An unexpected error occurred')
      setDebugInfo(`Unexpected error: ${err}`)
    }
    
    setIsLoading(false)
  }

  // Show loading state while checking auth
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Checking authentication...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{mode === 'signin' ? 'Sign in to your account' : 'Create a new account'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
            />
            {error && <div className="text-red-600 text-sm">{error}</div>}
            {success && <div className="text-green-600 text-sm">{success}</div>}
            {debugInfo && (
              <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
                <strong>Debug Info:</strong> {debugInfo}
              </div>
            )}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (mode === 'signin' ? 'Signing in...' : 'Signing up...') : (mode === 'signin' ? 'Sign In' : 'Sign Up')}
            </Button>
          </form>
          <div className="my-6 flex items-center justify-center gap-2">
            <span className="text-muted-foreground text-xs">
              {mode === 'signin' ? "Don't have an account?" : 'Already have an account?'}
            </span>
            <button
              type="button"
              className="text-primary text-xs underline"
              onClick={() => {
                setMode(mode === 'signin' ? 'signup' : 'signin')
                setError('')
                setSuccess('')
                setDebugInfo('')
              }}
            >
              {mode === 'signin' ? 'Sign Up' : 'Sign In'}
            </button>
          </div>
        </CardContent>
      </Card>
    </main>
  )
} 