'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/auth-provider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function HomePage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && user) {
      router.push('/dashboard')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-6">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <CardTitle className="text-4xl font-bold mb-4">
            Sales Opportunity Detection
          </CardTitle>
          <p className="text-muted-foreground text-lg">
            AI-driven sales opportunity detection between sent emails and Pipedrive CRM
          </p>
        </CardHeader>
        <CardContent className="text-center space-y-6">
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Features</h3>
            <div className="grid gap-4 md:grid-cols-2 text-left">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">📧 Email Integration</h4>
                <p className="text-sm text-muted-foreground">
                  Connect your Microsoft Outlook to monitor sent emails
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">📊 CRM Sync</h4>
                <p className="text-sm text-muted-foreground">
                  Integrate with Pipedrive to track deals and contacts
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">🤖 AI Analysis</h4>
                <p className="text-sm text-muted-foreground">
                  AI-powered opportunity detection and insights
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">📈 Real-time Updates</h4>
                <p className="text-sm text-muted-foreground">
                  Live activity monitoring and notifications
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex gap-4 justify-center">
            <Button onClick={() => router.push('/login')} size="lg">
              Get Started
            </Button>
            <Button variant="outline" onClick={() => router.push('/login')} size="lg">
              Sign In
            </Button>
          </div>
        </CardContent>
      </Card>
    </main>
  )
} 