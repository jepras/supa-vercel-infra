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
import { Loader2, Link, Unlink, Bell, BellOff } from 'lucide-react'

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

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function DashboardPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isConnecting, setIsConnecting] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'connected' | 'disconnected'>('unknown')
  const [microsoftConnectionStatus, setMicrosoftConnectionStatus] = useState<'unknown' | 'connected' | 'disconnected'>('unknown')
  const [testResult, setTestResult] = useState<string | null>(null)
  const [webhookSubscriptions, setWebhookSubscriptions] = useState<any[]>([])
  const [isCreatingWebhook, setIsCreatingWebhook] = useState(false)
  const [webhookStatus, setWebhookStatus] = useState<string | null>(null)
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
      checkConnectionStatus()
      checkMicrosoftConnectionStatus()
      fetchWebhookSubscriptions()
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

  async function handleConnectPipedrive() {
    try {
      setIsConnecting(true)
      
      // Get OAuth URL from backend (no auth required for connect)
      const response = await fetch(`${BACKEND_URL}/api/oauth/pipedrive/connect`)
      
      if (!response.ok) {
        throw new Error('Failed to get OAuth URL')
      }
      
      const data = await response.json()
      
      // Redirect to Pipedrive OAuth
      window.location.href = data.auth_url
    } catch (error) {
      console.error('Error connecting to Pipedrive:', error)
      alert('Failed to connect to Pipedrive. Please try again.')
    } finally {
      setIsConnecting(false)
    }
  }

  async function handleConnectMicrosoft() {
    try {
      setIsConnecting(true)
      
      // Get OAuth URL from backend (no auth required for connect)
      const response = await fetch(`${BACKEND_URL}/api/oauth/microsoft/connect`)
      
      if (!response.ok) {
        throw new Error('Failed to get OAuth URL')
      }
      
      const data = await response.json()
      
      // Redirect to Microsoft OAuth
      window.location.href = data.auth_url
    } catch (error) {
      console.error('Error connecting to Microsoft:', error)
      alert('Failed to connect to Microsoft. Please try again.')
    } finally {
      setIsConnecting(false)
    }
  }

  async function checkConnectionStatus() {
    try {
      // Get session token for authentication
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        console.error('No session token available for status check')
        setConnectionStatus('disconnected')
        return
      }
      
      const response = await fetch(`${BACKEND_URL}/api/oauth/pipedrive/status`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setConnectionStatus(data.connected ? 'connected' : 'disconnected')
      } else {
        console.error('Status check failed:', response.status)
        setConnectionStatus('disconnected')
      }
    } catch (error) {
      console.error('Error checking connection status:', error)
      setConnectionStatus('disconnected')
    }
  }

  async function fetchWebhookSubscriptions() {
    if (!user) return
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        console.error('No session token available for webhook fetch')
        return
      }
      
      const response = await fetch(`${BACKEND_URL}/api/webhooks/microsoft/subscriptions/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setWebhookSubscriptions(data.subscriptions || [])
      } else {
        console.error('Failed to fetch webhook subscriptions:', response.status)
        setWebhookSubscriptions([])
      }
    } catch (error) {
      console.error('Error fetching webhook subscriptions:', error)
      setWebhookSubscriptions([])
    }
  }

  async function createWebhookSubscription() {
    if (!user) return
    
    try {
      setIsCreatingWebhook(true)
      setWebhookStatus(null)
      
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        throw new Error('No session token available')
      }
      
      // Use Railway production URL for webhook notifications
      const notificationUrl = `${BACKEND_URL}/api/webhooks/microsoft/email`
      
      const response = await fetch(`${BACKEND_URL}/api/webhooks/microsoft/subscribe`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          notification_url: notificationUrl
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setWebhookStatus('✅ Webhook subscription created successfully!')
        fetchWebhookSubscriptions() // Refresh the list
      } else {
        const errorData = await response.json()
        setWebhookStatus(`❌ Failed to create webhook: ${errorData.detail || response.statusText}`)
      }
    } catch (error) {
      console.error('Error creating webhook subscription:', error)
      setWebhookStatus(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsCreatingWebhook(false)
    }
  }

  async function deleteWebhookSubscription(subscriptionId: string) {
    if (!user) return
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        throw new Error('No session token available')
      }
      
      const response = await fetch(`${BACKEND_URL}/api/webhooks/microsoft/subscriptions/${user.id}/${subscriptionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        setWebhookStatus('✅ Webhook subscription deleted successfully!')
        fetchWebhookSubscriptions() // Refresh the list
      } else {
        const errorData = await response.json()
        setWebhookStatus(`❌ Failed to delete webhook: ${errorData.detail || response.statusText}`)
      }
    } catch (error) {
      console.error('Error deleting webhook subscription:', error)
      setWebhookStatus(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  async function checkMicrosoftConnectionStatus() {
    try {
      // Get session token for authentication
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        console.error('No session token available for Microsoft status check')
        setMicrosoftConnectionStatus('disconnected')
        return
      }
      
      const response = await fetch(`${BACKEND_URL}/api/oauth/microsoft/status`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setMicrosoftConnectionStatus(data.connected ? 'connected' : 'disconnected')
      } else {
        console.error('Microsoft status check failed:', response.status)
        setMicrosoftConnectionStatus('disconnected')
      }
    } catch (error) {
      console.error('Error checking Microsoft connection status:', error)
      setMicrosoftConnectionStatus('disconnected')
    }
  }

  async function testPipedriveConnection() {
    try {
      setIsTesting(true)
      setTestResult(null)
      
      // Get session token for authentication
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        throw new Error('Not authenticated')
      }
      
      const response = await fetch(`${BACKEND_URL}/api/oauth/pipedrive/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setTestResult(`✅ ${data.message}\n👤 Name: ${data.user_info.name}\n📧 Email: ${data.user_info.email}\n🏢 Company: ${data.user_info.company}`)
      } else {
        setTestResult(`❌ ${data.detail || 'Test failed'}`)
      }
    } catch (error) {
      console.error('Error testing Pipedrive connection:', error)
      setTestResult(`❌ ${error instanceof Error ? error.message : 'Test failed'}`)
    } finally {
      setIsTesting(false)
    }
  }

  async function testMicrosoftConnection() {
    try {
      setIsTesting(true)
      setTestResult(null)
      
      // Get session token for authentication
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        throw new Error('Not authenticated')
      }
      
      const response = await fetch(`${BACKEND_URL}/api/oauth/microsoft/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setTestResult(`✅ ${data.message}\n👤 Name: ${data.user_info.name}\n📧 Email: ${data.user_info.email}\n🆔 ID: ${data.user_info.id}`)
      } else {
        setTestResult(`❌ ${data.detail || 'Test failed'}`)
      }
    } catch (error) {
      console.error('Error testing Microsoft connection:', error)
      setTestResult(`❌ ${error instanceof Error ? error.message : 'Test failed'}`)
    } finally {
      setIsTesting(false)
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
      case 'microsoft':
        return 'Microsoft Outlook'
      default:
        return provider
    }
  }

  function getProviderDescription(provider: string) {
    switch (provider) {
      case 'pipedrive':
        return 'CRM integration for deal management'
      case 'microsoft':
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
                    <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                      <span className="text-orange-600 font-bold text-sm">P</span>
                    </div>
                    Pipedrive Integration
                  </CardTitle>
                  <CardDescription>
                    Connect your Pipedrive account to automatically create deals from email opportunities
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={microsoftConnectionStatus === 'connected' ? 'default' : 'secondary'}
                      className={microsoftConnectionStatus === 'connected' ? 'bg-green-100 text-green-800' : ''}
                    >
                      {microsoftConnectionStatus === 'connected' && <Link className="h-3 w-3 mr-1" />}
                      {microsoftConnectionStatus === 'disconnected' && <Unlink className="h-3 w-3 mr-1" />}
                      {microsoftConnectionStatus === 'connected' ? 'Connected' : 'Not Connected'}
                    </Badge>
                  </div>

                  <Button 
                    onClick={handleConnectPipedrive}
                    disabled={isConnecting}
                    className="w-full"
                  >
                    {isConnecting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Link className="h-4 w-4 mr-2" />
                        Connect Pipedrive
                      </>
                    )}
                  </Button>

                  <Button 
                    onClick={checkConnectionStatus}
                    variant="outline"
                    className="w-full"
                  >
                    Refresh Status
                  </Button>

                  {connectionStatus === 'connected' && (
                    <>
                      <Button 
                        onClick={testPipedriveConnection}
                        disabled={isTesting}
                        variant="outline"
                        className="w-full"
                      >
                        {isTesting ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          'Test Pipedrive API'
                        )}
                      </Button>
                      
                      {testResult && (
                        <div className="mt-2 p-3 bg-gray-900 border border-gray-700 rounded-md">
                          <pre className="text-xs whitespace-pre-wrap text-gray-100">{testResult}</pre>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Microsoft Integration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-blue-600 font-bold text-sm">O</span>
                    </div>
                    Microsoft Outlook Integration
                  </CardTitle>
                  <CardDescription>
                    Connect your Microsoft Outlook account to monitor emails for sales opportunities
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={connectionStatus === 'connected' ? 'default' : 'secondary'}
                      className={connectionStatus === 'connected' ? 'bg-green-100 text-green-800' : ''}
                    >
                      {connectionStatus === 'connected' && <Link className="h-3 w-3 mr-1" />}
                      {connectionStatus === 'disconnected' && <Unlink className="h-3 w-3 mr-1" />}
                      {connectionStatus === 'connected' ? 'Connected' : 'Not Connected'}
                    </Badge>
                  </div>

                  <Button 
                    onClick={handleConnectMicrosoft}
                    disabled={isConnecting}
                    className="w-full"
                  >
                    {isConnecting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Link className="h-4 w-4 mr-2" />
                        Connect Microsoft Outlook
                      </>
                    )}
                  </Button>

                  <Button 
                    onClick={checkMicrosoftConnectionStatus}
                    variant="outline"
                    className="w-full"
                  >
                    Refresh Status
                  </Button>

                  {microsoftConnectionStatus === 'connected' && (
                    <>
                      <Button 
                        onClick={testMicrosoftConnection}
                        disabled={isTesting}
                        variant="outline"
                        className="w-full"
                      >
                        {isTesting ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          'Test Microsoft Graph API'
                        )}
                      </Button>
                      
                      {testResult && (
                        <div className="mt-2 p-3 bg-gray-900 border border-gray-700 rounded-md">
                          <pre className="text-xs whitespace-pre-wrap text-gray-100">{testResult}</pre>
                        </div>
                      )}

                      {/* Webhook Subscriptions Section */}
                      <div className="border-t pt-4 mt-4">
                        <h4 className="font-medium mb-3">Email Webhooks</h4>
                        
                        {webhookSubscriptions.length > 0 ? (
                          <div className="space-y-2">
                            {webhookSubscriptions.map((subscription) => (
                              <div key={subscription.subscription_id} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <Bell className="h-4 w-4 text-green-600" />
                                    <span className="text-sm font-medium">Active Webhook</span>
                                    <Badge variant="outline" className="text-xs">
                                      {subscription.is_active ? 'Active' : 'Inactive'}
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Expires: {new Date(subscription.expiration_date).toLocaleDateString()}
                                  </p>
                                </div>
                                <Button
                                  onClick={() => deleteWebhookSubscription(subscription.subscription_id)}
                                  variant="outline"
                                  size="sm"
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <BellOff className="h-4 w-4" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-4">
                            <BellOff className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                            <p className="text-sm text-muted-foreground mb-3">
                              No webhook subscriptions active
                            </p>
                            <Button 
                              onClick={createWebhookSubscription}
                              disabled={isCreatingWebhook}
                              size="sm"
                              className="w-full"
                            >
                              {isCreatingWebhook ? (
                                <>
                                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  Creating Webhook...
                                </>
                              ) : (
                                <>
                                  <Bell className="h-4 w-4 mr-2" />
                                  Enable Email Webhooks
                                </>
                              )}
                            </Button>
                          </div>
                        )}

                        {webhookStatus && (
                          <div className={`mt-3 p-3 rounded-md text-sm ${
                            webhookStatus.includes('✅') 
                              ? 'bg-green-50 text-green-800 border border-green-200' 
                              : 'bg-red-50 text-red-800 border border-red-200'
                          }`}>
                            {webhookStatus}
                          </div>
                        )}
                      </div>
                    </>
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