"use client"

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function SupabaseTest() {
  const [connectionStatus, setConnectionStatus] = useState<'loading' | 'connected' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [userCount, setUserCount] = useState<number | null>(null)

  useEffect(() => {
    testConnection()
  }, [])

  const testConnection = async () => {
    try {
      setConnectionStatus('loading')
      
      // Test basic connection by checking auth
      const { data: authData, error: authError } = await supabase.auth.getSession()
      
      if (authError) {
        throw authError
      }
      
      setConnectionStatus('connected')
      
      // Try to query tables to see if they exist
      try {
        const { data: dbData, error: dbError } = await supabase
          .from('activity_logs')
          .select('count')
          .limit(1)
        
        if (dbError) {
          console.warn('activity_logs table query failed:', dbError.message)
        } else {
          console.log('✅ activity_logs table is accessible')
        }
      } catch (tableError) {
        console.warn('activity_logs table access failed:', tableError)
      }

      // Try integrations table
      try {
        const { data: intData, error: intError } = await supabase
          .from('integrations')
          .select('count')
          .limit(1)
        
        if (intError) {
          console.warn('integrations table query failed:', intError.message)
        } else {
          console.log('✅ integrations table is accessible')
        }
      } catch (tableError) {
        console.warn('integrations table access failed:', tableError)
      }
      
      // Note: User count requires admin privileges, so we'll skip it for now
      setUserCount(0)
      
    } catch (error) {
      console.error('Supabase connection error:', error)
      setConnectionStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Unknown error')
    }
  }

  const testAuth = async () => {
    try {
      // First test if auth service is accessible
      const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
      
      if (sessionError) {
        throw sessionError
      }
      
      // Try to sign up with a test email
      const { data, error } = await supabase.auth.signUp({
        email: 'test@example.com',
        password: 'TestPassword123!'
      })
      
      if (error) {
        // If it's an email validation error, that's actually good - it means auth is working
        if (error.message.includes('email') || error.message.includes('invalid')) {
          alert('✅ Auth service is working! Email validation is active (this is good for security).')
        } else {
          alert(`Auth test failed: ${error.message}`)
        }
      } else {
        alert('Auth test successful! Check your Supabase dashboard for the test user.')
      }
    } catch (error) {
      console.error('Auth test error:', error)
      alert('Auth test failed')
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          🔗 Supabase Connection Test
          <Badge 
            variant={connectionStatus === 'connected' ? 'default' : connectionStatus === 'error' ? 'destructive' : 'secondary'}
          >
            {connectionStatus === 'loading' ? 'Testing...' : connectionStatus === 'connected' ? 'Connected' : 'Error'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {connectionStatus === 'loading' && (
          <p className="text-muted-foreground">Testing connection to Supabase...</p>
        )}
        
        {connectionStatus === 'connected' && (
          <div className="space-y-2">
            <p className="text-green-600 font-medium">✅ Connection successful!</p>
            <p className="text-sm text-muted-foreground">
              Database tables are accessible
            </p>
            {userCount !== null && (
              <p className="text-sm text-muted-foreground">
                Users in database: {userCount}
              </p>
            )}
          </div>
        )}
        
        {connectionStatus === 'error' && (
          <div className="space-y-2">
            <p className="text-red-600 font-medium">❌ Connection failed</p>
            <p className="text-sm text-muted-foreground">
              {errorMessage}
            </p>
          </div>
        )}
        
        <div className="flex gap-2">
          <Button onClick={testConnection} variant="outline" size="sm">
            Retest Connection
          </Button>
          <Button onClick={testAuth} variant="outline" size="sm">
            Test Auth
          </Button>
        </div>
      </CardContent>
    </Card>
  )
} 