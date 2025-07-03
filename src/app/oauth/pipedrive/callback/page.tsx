'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2, CheckCircle, XCircle, ArrowLeft } from 'lucide-react'
import { useAuth } from '@/components/auth-provider'

interface OAuthResponse {
  status: string
  message: string
  user_id?: string
}

function OAuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { session } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('Processing OAuth callback...')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Wait for session to be available before proceeding
    if (session !== undefined) {
      handleOAuthCallback()
    }
  }, [session])

  async function handleOAuthCallback() {
    try {
      console.log('OAuth callback - Session available:', !!session)
      console.log('OAuth callback - Session access token:', !!session?.access_token)
      
      // Get OAuth parameters from URL
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')

      if (error) {
        setStatus('error')
        setMessage('OAuth authorization was denied or failed')
        setError(error)
        return
      }

      if (!code) {
        setStatus('error')
        setMessage('Authorization code not provided')
        setError('Missing authorization code')
        return
      }

      if (!session?.access_token) {
        setStatus('error')
        setMessage('Not authenticated')
        setError('Please log in to connect Pipedrive')
        return
      }

      // Prepare headers with authentication
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      
      // Add Authorization header if we have a session
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`
        console.log('OAuth callback - Added Authorization header')
      } else {
        console.log('OAuth callback - No session token available')
      }
      
      // Call backend to exchange code for tokens
      const response = await fetch('/api/oauth/pipedrive/callback', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          code,
          state,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to complete OAuth flow')
      }

      const data: OAuthResponse = await response.json()

      if (data.status === 'success') {
        setStatus('success')
        setMessage(data.message)
      } else {
        throw new Error(data.message || 'OAuth flow failed')
      }
    } catch (err) {
      setStatus('error')
      setMessage('Failed to complete OAuth flow')
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  function handleBackToDashboard() {
    router.push('/dashboard')
  }

  function handleRetry() {
    setStatus('loading')
    setMessage('Processing OAuth callback...')
    setError(null)
    handleOAuthCallback()
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            {status === 'loading' && <Loader2 className="h-6 w-6 animate-spin" />}
            {status === 'success' && <CheckCircle className="h-6 w-6 text-green-600" />}
            {status === 'error' && <XCircle className="h-6 w-6 text-red-600" />}
            Pipedrive OAuth
          </CardTitle>
          <CardDescription>
            {status === 'loading' && 'Completing OAuth authorization...'}
            {status === 'success' && 'Successfully connected to Pipedrive'}
            {status === 'error' && 'Failed to connect to Pipedrive'}
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">{message}</p>
            
            {status === 'success' && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Connected Successfully
              </Badge>
            )}
            
            {status === 'error' && error && (
              <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={handleBackToDashboard}
              variant="outline"
              className="flex-1"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            
            {status === 'error' && (
              <Button 
                onClick={handleRetry}
                className="flex-1"
              >
                Retry
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function PipedriveCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              Pipedrive OAuth
            </CardTitle>
            <CardDescription>
              Loading OAuth callback...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    }>
      <OAuthCallbackContent />
    </Suspense>
  )
} 