'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/auth-provider'
import { ConnectivityTest } from '@/components/connectivity-test'

interface Integration {
  id: string
  provider: string
  provider_user_email: string
  is_active: boolean
  created_at: string
  last_sync_at: string | null
}

interface ActivityLog {
  id: string
  activity_type: string
  status: string
  message: string
  created_at: string
  metadata: any
}

export default function DashboardPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isConnecting, setIsConnecting] = useState<string | null>(null)
  const router = useRouter()
  const { user, isLoading: authLoading, signOut } = useAuth()

  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        console.log('No user found, redirecting to login')
        router.push('/login')
        return
      }
      
      console.log('User authenticated:', user.email)
      fetchIntegrations()
      fetchActivityLogs()
      subscribeToActivityLogs()
      setIsLoading(false)
    }
  }, [user, authLoading, router])

  async function fetchIntegrations() {
    if (!user) return
    
    const { data, error } = await supabase
      .from('integrations')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching integrations:', error)
      return
    }

    setIntegrations(data || [])
  }

  async function fetchActivityLogs() {
    if (!user) return
    
    const { data, error } = await supabase
      .from('activity_logs')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(50)

    if (error) {
      console.error('Error fetching activity logs:', error)
      return
    }

    setActivityLogs(data || [])
  }

  function subscribeToActivityLogs() {
    if (!user) return
    
    const subscription = supabase
      .channel('activity_logs')
      .on('postgres_changes', 
        { 
          event: 'INSERT', 
          schema: 'public', 
          table: 'activity_logs',
          filter: `user_id=eq.${user.id}`
        }, 
        (payload) => {
          setActivityLogs(prev => [payload.new as ActivityLog, ...prev.slice(0, 49)])
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }

  async function initiateOAuth(provider: string) {
    if (!user) return
    
    setIsConnecting(provider)
    try {
      const response = await fetch(`/api/oauth/${provider}/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to initiate OAuth')
      }

      const { auth_url } = await response.json()
      
      // Open OAuth window
      const oauthWindow = window.open(
        auth_url,
        `${provider}_oauth`,
        'width=500,height=600,scrollbars=yes,resizable=yes'
      )

      // Listen for OAuth completion
      const handleMessage = (event: MessageEvent) => {
        if (event.data.type === 'oauth_success' && event.data.provider === provider) {
          oauthWindow?.close()
          window.removeEventListener('message', handleMessage)
          fetchIntegrations()
          setIsConnecting(null)
        }
      }

      window.addEventListener('message', handleMessage)

      // Fallback: check if window was closed
      const checkClosed = setInterval(() => {
        if (oauthWindow?.closed) {
          clearInterval(checkClosed)
          window.removeEventListener('message', handleMessage)
          fetchIntegrations()
          setIsConnecting(null)
        }
      }, 1000)

    } catch (error) {
      console.error(`Error initiating ${provider} OAuth:`, error)
      setIsConnecting(null)
    }
  }

  async function disconnectIntegration(integrationId: string) {
    try {
      const { error } = await supabase
        .from('integrations')
        .delete()
        .eq('id', integrationId)

      if (error) throw error

      fetchIntegrations()
    } catch (error) {
      console.error('Error disconnecting integration:', error)
    }
  }

  function getProviderDisplayName(provider: string) {
    switch (provider) {
      case 'pipedrive':
        return 'Pipedrive'
      case 'azure':
        return 'Microsoft Outlook'
      default:
        return provider
    }
  }

  function getProviderDescription(provider: string) {
    switch (provider) {
      case 'pipedrive':
        return 'CRM integration for deal management'
      case 'azure':
        return 'Email automation and webhook processing'
      default:
        return 'Integration'
    }
  }

  // Show loading state while checking auth
  if (authLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Show user info and debug info
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header with user info and sign out */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back, {user?.email}
            </p>
            <div className="text-xs text-muted-foreground mt-1">
              User ID: {user?.id} | Email confirmed: {user?.email_confirmed_at ? 'Yes' : 'No'}
            </div>
          </div>
          <Button variant="outline" onClick={signOut}>
            Sign Out
          </Button>
        </div>

        <Tabs defaultValue="integrations" className="space-y-6">
          <TabsList>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            <TabsTrigger value="activity">Activity Logs</TabsTrigger>
            <TabsTrigger value="connectivity">Connectivity Test</TabsTrigger>
          </TabsList>

          <TabsContent value="integrations" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              {/* Pipedrive Integration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span>Pipedrive</span>
                    {integrations.find(i => i.provider === 'pipedrive') && (
                      <Badge variant="secondary">Connected</Badge>
                    )}
                  </CardTitle>
                  <CardDescription>
                    Connect your Pipedrive CRM to sync deals and contacts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {integrations.find(i => i.provider === 'pipedrive') ? (
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        Connected as: {integrations.find(i => i.provider === 'pipedrive')?.provider_user_email}
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => disconnectIntegration(integrations.find(i => i.provider === 'pipedrive')!.id)}
                      >
                        Disconnect
                      </Button>
                    </div>
                  ) : (
                    <Button
                      onClick={() => initiateOAuth('pipedrive')}
                      disabled={isConnecting === 'pipedrive'}
                    >
                      {isConnecting === 'pipedrive' ? 'Connecting...' : 'Connect Pipedrive'}
                    </Button>
                  )}
                </CardContent>
              </Card>

              {/* Azure Integration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span>Microsoft Outlook</span>
                    {integrations.find(i => i.provider === 'azure') && (
                      <Badge variant="secondary">Connected</Badge>
                    )}
                  </CardTitle>
                  <CardDescription>
                    Connect your Microsoft Outlook for email automation
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {integrations.find(i => i.provider === 'azure') ? (
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        Connected as: {integrations.find(i => i.provider === 'azure')?.provider_user_email}
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => disconnectIntegration(integrations.find(i => i.provider === 'azure')!.id)}
                      >
                        Disconnect
                      </Button>
                    </div>
                  ) : (
                    <Button
                      onClick={() => initiateOAuth('azure')}
                      disabled={isConnecting === 'azure'}
                    >
                      {isConnecting === 'azure' ? 'Connecting...' : 'Connect Outlook'}
                    </Button>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="activity" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Latest activity from your integrations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {activityLogs.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    No activity logs yet. Connect an integration to see activity.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {activityLogs.map((log) => (
                      <div key={log.id} className="flex items-start gap-4 p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant={log.status === 'success' ? 'default' : 'destructive'}>
                              {log.status}
                            </Badge>
                            <span className="text-sm font-medium">{log.activity_type}</span>
                          </div>
                          <p className="text-sm text-muted-foreground">{log.message}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(log.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="connectivity" className="space-y-4">
            <ConnectivityTest />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
} 