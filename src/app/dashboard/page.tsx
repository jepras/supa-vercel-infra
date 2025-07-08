'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/auth-provider'
import { MonitoringDashboard } from '@/components/monitoring/monitoring-dashboard'
import { MonitoringProvider } from '@/components/monitoring/monitoring-context'
import { LogsDashboard } from '@/components/logs/logs-dashboard'
import { Loader2, Link, Unlink, Bell, BellOff } from 'lucide-react'

interface Integration {
  id: string
  provider: string
  provider_user_email: string
  is_active: boolean
  created_at: string
  last_sync_at: string | null
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function DashboardPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isConnecting, setIsConnecting] = useState(false)
  const [isTestingPipedrive, setIsTestingPipedrive] = useState(false)
  const [isTestingMicrosoft, setIsTestingMicrosoft] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading')
  const [microsoftConnectionStatus, setMicrosoftConnectionStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading')
  const [pipedriveTestResult, setPipedriveTestResult] = useState<string | null>(null)
  const [microsoftTestResult, setMicrosoftTestResult] = useState<string | null>(null)
  const [webhookSubscriptions, setWebhookSubscriptions] = useState<any[]>([])
  const [isCreatingWebhook, setIsCreatingWebhook] = useState(false)
  const [webhookStatus, setWebhookStatus] = useState<string | null>(null)
  const [webhookProcessingStatus, setWebhookProcessingStatus] = useState<any>(null)
  const [isLoadingWebhookStatus, setIsLoadingWebhookStatus] = useState(false)
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
      checkConnectionStatus()
      checkMicrosoftConnectionStatus()
      fetchWebhookSubscriptions()
      fetchWebhookProcessingStatus()
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
      setConnectionStatus('loading')
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

  async function fetchWebhookProcessingStatus() {
    if (!user) return
    
    try {
      setIsLoadingWebhookStatus(true)
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.access_token) {
        console.error('No session token available for webhook status fetch')
        return
      }
      
      const response = await fetch(`${BACKEND_URL}/api/webhooks/microsoft/status/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setWebhookProcessingStatus(data)
      } else {
        console.error('Failed to fetch webhook processing status:', response.status)
        setWebhookProcessingStatus(null)
      }
    } catch (error) {
      console.error('Error fetching webhook processing status:', error)
      setWebhookProcessingStatus(null)
    } finally {
      setIsLoadingWebhookStatus(false)
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
      
      const response = await fetch(`${BACKEND_URL}/api/webhooks/microsoft/unsubscribe`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          subscription_id: subscriptionId
        })
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
      setMicrosoftConnectionStatus('loading')
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
      setIsTestingPipedrive(true)
      setPipedriveTestResult(null)
      
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
        setPipedriveTestResult(`✅ ${data.message}\n👤 Name: ${data.user_info.name}\n📧 Email: ${data.user_info.email}\n🏢 Company: ${data.user_info.company}`)
      } else {
        setPipedriveTestResult(`❌ ${data.detail || 'Test failed'}`)
      }
    } catch (error) {
      console.error('Error testing Pipedrive connection:', error)
      setPipedriveTestResult(`❌ ${error instanceof Error ? error.message : 'Test failed'}`)
    } finally {
      setIsTestingPipedrive(false)
    }
  }

  async function testMicrosoftConnection() {
    try {
      setIsTestingMicrosoft(true)
      setMicrosoftTestResult(null)
      
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
        setMicrosoftTestResult(`✅ ${data.message}\n👤 Name: ${data.user_info.name}\n📧 Email: ${data.user_info.email}\n🆔 ID: ${data.user_info.id}`)
      } else {
        setMicrosoftTestResult(`❌ ${data.detail || 'Test failed'}`)
      }
    } catch (error) {
      console.error('Error testing Microsoft connection:', error)
      setMicrosoftTestResult(`❌ ${error instanceof Error ? error.message : 'Test failed'}`)
    } finally {
      setIsTestingMicrosoft(false)
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

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              Loading Dashboard
            </CardTitle>
            <CardDescription>
              Please wait while we load your dashboard...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-2">Welcome back, {user?.email}</p>
          </div>
          <Button onClick={signOut} variant="outline">
            Sign Out
          </Button>
        </div>

        <Tabs defaultValue="integrations" className="space-y-6">
          <TabsList>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
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
                    {connectionStatus === 'loading' ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span className="text-sm text-muted-foreground">Checking status...</span>
                      </div>
                    ) : (
                      <Badge 
                        variant={connectionStatus === 'connected' ? 'default' : 'secondary'}
                        className={connectionStatus === 'connected' ? 'bg-green-100 text-green-800' : ''}
                      >
                        {connectionStatus === 'connected' && <Link className="h-3 w-3 mr-1" />}
                        {connectionStatus === 'disconnected' && <Unlink className="h-3 w-3 mr-1" />}
                        {connectionStatus === 'connected' ? 'Connected' : 'Not Connected'}
                      </Badge>
                    )}
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

                  {connectionStatus === 'connected' && (
                    <>
                      <Button 
                        onClick={testPipedriveConnection}
                        disabled={isTestingPipedrive}
                        variant="outline"
                        className="w-full"
                      >
                        {isTestingPipedrive ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          'Test Pipedrive API'
                        )}
                      </Button>
                      
                      {pipedriveTestResult && (
                        <div className="mt-2 p-3 bg-gray-900 border border-gray-700 rounded-md">
                          <pre className="text-xs whitespace-pre-wrap text-gray-100">{pipedriveTestResult}</pre>
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
                    {microsoftConnectionStatus === 'loading' ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span className="text-sm text-muted-foreground">Checking status...</span>
                      </div>
                    ) : (
                      <Badge 
                        variant={microsoftConnectionStatus === 'connected' ? 'default' : 'secondary'}
                        className={microsoftConnectionStatus === 'connected' ? 'bg-green-100 text-green-800' : ''}
                      >
                        {microsoftConnectionStatus === 'connected' && <Link className="h-3 w-3 mr-1" />}
                        {microsoftConnectionStatus === 'disconnected' && <Unlink className="h-3 w-3 mr-1" />}
                        {microsoftConnectionStatus === 'connected' ? 'Connected' : 'Not Connected'}
                      </Badge>
                    )}
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

                  {microsoftConnectionStatus === 'connected' && (
                    <>
                      <Button 
                        onClick={testMicrosoftConnection}
                        disabled={isTestingMicrosoft}
                        variant="outline"
                        className="w-full"
                      >
                        {isTestingMicrosoft ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          'Test Microsoft Graph API'
                        )}
                      </Button>
                      
                      {microsoftTestResult && (
                        <div className="mt-2 p-3 bg-gray-900 border border-gray-700 rounded-md">
                          <pre className="text-xs whitespace-pre-wrap text-gray-100">{microsoftTestResult}</pre>
                        </div>
                      )}

                      {/* Webhook Subscriptions Section */}
                      <div className="border-t pt-4 mt-4">
                        <h4 className="font-medium mb-3">Email Webhooks</h4>
                        
                        {webhookSubscriptions.length > 0 ? (
                          <div className="space-y-2">
                            {webhookSubscriptions.map((subscription) => (
                              <div key={subscription.subscription_id} className="flex items-center justify-between p-4 rounded-xl border border-border shadow-sm">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <Bell className="h-5 w-5 text-green-600" />
                                    <span className="text-base font-medium text-foreground">Active Webhook</span>
                                    <Badge variant="outline" className="text-xs">
                                      {subscription.is_active ? 'Active' : 'Inactive'}
                                    </Badge>
                                  </div>
                                  <p className="text-sm text-muted-foreground mt-2">
                                    Expires: {new Date(subscription.expiration_date).toLocaleDateString()}
                                  </p>
                                </div>
                                <Button
                                  onClick={() => deleteWebhookSubscription(subscription.subscription_id)}
                                  variant="ghost"
                                  size="icon"
                                  className="text-red-600 hover:text-red-700 bg-transparent"
                                >
                                  <BellOff className="h-5 w-5" />
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
                              ? 'bg-green-950/50 text-green-400 border border-green-800' 
                              : 'bg-red-950/50 text-red-400 border border-red-800'
                          }`}>
                            {webhookStatus}
                          </div>
                        )}

                        {/* Webhook Processing Status Section */}
                        {webhookSubscriptions.length > 0 && (
                          <div className="border-t pt-4 mt-4">
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="font-medium">Processing Status</h4>
                              <Button
                                onClick={fetchWebhookProcessingStatus}
                                disabled={isLoadingWebhookStatus}
                                variant="outline"
                                size="sm"
                              >
                                {isLoadingWebhookStatus ? (
                                  <Loader2 className="h-3 w-3 animate-spin" />
                                ) : (
                                  'Refresh'
                                )}
                              </Button>
                            </div>
                            
                            {webhookProcessingStatus ? (
                              <div className="space-y-3">
                                <div className="grid grid-cols-3 gap-2 text-sm">
                                  <div className="text-center p-2 bg-blue-950/50 rounded-md border border-blue-800/50">
                                    <div className="font-semibold text-blue-400">
                                      {webhookProcessingStatus.recent_processing?.total_emails || 0}
                                    </div>
                                    <div className="text-xs text-blue-300">Total Emails</div>
                                  </div>
                                  <div className="text-center p-2 bg-green-950/50 rounded-md border border-green-800/50">
                                    <div className="font-semibold text-green-400">
                                      {webhookProcessingStatus.recent_processing?.ai_processed || 0}
                                    </div>
                                    <div className="text-xs text-green-300">AI Processed</div>
                                  </div>
                                  <div className="text-center p-2 bg-purple-950/50 rounded-md border border-purple-800/50">
                                    <div className="font-semibold text-purple-400">
                                      {webhookProcessingStatus.recent_processing?.opportunities_detected || 0}
                                    </div>
                                    <div className="text-xs text-purple-300">Opportunities</div>
                                  </div>
                                </div>
                                
                                {webhookProcessingStatus.recent_processing?.recent_emails && 
                                 webhookProcessingStatus.recent_processing.recent_emails.length > 0 && (
                                  <div className="space-y-2">
                                    <h5 className="text-sm font-medium text-foreground">Recent Emails</h5>
                                    {webhookProcessingStatus.recent_processing.recent_emails.slice(0, 3).map((email: any) => (
                                      <div key={email.id} className="p-2 bg-muted rounded-md text-xs border border-border">
                                        <div className="flex items-center justify-between">
                                          <div className="flex-1">
                                            <div className="font-medium truncate text-foreground">{email.subject || 'No Subject'}</div>
                                            <div className="text-muted-foreground truncate">
                                              To: {email.recipient_emails?.[0] || 'Unknown'}
                                            </div>
                                          </div>
                                          <div className="flex items-center gap-1 ml-2">
                                            {email.ai_analyzed && (
                                              <Badge variant="outline" className="text-xs bg-green-950/50 text-green-400 border-green-800">
                                                AI
                                              </Badge>
                                            )}
                                            {email.opportunity_detected && (
                                              <Badge variant="outline" className="text-xs bg-purple-950/50 text-purple-400 border-purple-800">
                                                Deal
                                              </Badge>
                                            )}
                                          </div>
                                        </div>
                                        <div className="text-muted-foreground mt-1">
                                          {new Date(email.webhook_received_at).toLocaleString()}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="text-center py-4 text-sm text-muted-foreground">
                                {isLoadingWebhookStatus ? (
                                  <div className="flex items-center justify-center gap-2">
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                    Loading processing status...
                                  </div>
                                ) : (
                                  'No processing data available'
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <LogsDashboard />
          </TabsContent>

          <TabsContent value="monitoring" className="space-y-4">
            <MonitoringProvider>
              <MonitoringDashboard />
            </MonitoringProvider>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
} 