'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ChevronLeft, ChevronRight, Mail, Activity, DollarSign, User, Building } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/components/auth-provider'

interface OpportunityLog {
  id: string
  sender_email: string
  recipient_email: string
  subject: string
  opportunity_detected: boolean
  confidence_score: number
  reasoning: string
  metadata: any
  created_at: string
}

interface ActivityLog {
  id: string
  activity_type: string
  description: string
  status: string
  metadata: any
  created_at: string
}

export function LogsDashboard() {
  // Logs dashboard component for displaying opportunity and activity logs
  const { user } = useAuth()
  const [opportunityLogs, setOpportunityLogs] = useState<OpportunityLog[]>([])
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([])
  const [loading, setLoading] = useState(true)
  const [opportunityPage, setOpportunityPage] = useState(1)
  const [activityPage, setActivityPage] = useState(1)
  const [opportunityTotal, setOpportunityTotal] = useState(0)
  const [activityTotal, setActivityTotal] = useState(0)
  const itemsPerPage = 10

  useEffect(() => {
    if (user) {
      fetchOpportunityLogs()
      fetchActivityLogs()
    }
  }, [user, opportunityPage, activityPage])

  async function fetchOpportunityLogs() {
    if (!user) return

    const from = (opportunityPage - 1) * itemsPerPage
    const to = from + itemsPerPage - 1

    // Get total count
    const { count } = await supabase
      .from('opportunity_logs')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)

    setOpportunityTotal(count || 0)

    // Get paginated data
    const { data, error } = await supabase
      .from('opportunity_logs')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .range(from, to)

    if (error) {
      console.error('Error fetching opportunity logs:', error)
      return
    }

    setOpportunityLogs(data || [])
  }

  async function fetchActivityLogs() {
    if (!user) return

    const from = (activityPage - 1) * itemsPerPage
    const to = from + itemsPerPage - 1

    // Get total count
    const { count } = await supabase
      .from('activity_logs')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)

    setActivityTotal(count || 0)

    // Get paginated data
    const { data, error } = await supabase
      .from('activity_logs')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .range(from, to)

    if (error) {
      console.error('Error fetching activity logs:', error)
      return
    }

    setActivityLogs(data || [])
    setLoading(false)
  }

  function getOpportunityStatus(opportunity: OpportunityLog) {
    if (opportunity.opportunity_detected) {
      return { label: 'Opportunity Detected', color: 'bg-green-100 text-green-800' }
    }
    return { label: 'No Opportunity', color: 'bg-gray-100 text-gray-800' }
  }

  function getActivityStatus(status: string) {
    switch (status) {
      case 'success':
        return { label: 'Success', color: 'bg-green-100 text-green-800' }
      case 'error':
        return { label: 'Error', color: 'bg-red-100 text-red-800' }
      case 'warning':
        return { label: 'Warning', color: 'bg-yellow-100 text-yellow-800' }
      default:
        return { label: 'Pending', color: 'bg-blue-100 text-blue-800' }
    }
  }

  function getActivityOutcome(activity: ActivityLog) {
    const metadata = activity.metadata || {}
    
    if (activity.activity_type === 'email_analyzed') {
      if (metadata.deal_created) return 'Deal Created'
      if (metadata.deal_ignored) return 'Deal Ignored'
      if (metadata.skipped) return 'Skipped'
      return 'Analyzed'
    }
    
    if (activity.activity_type === 'deal_created') {
      return `Deal Created: ${metadata.deal_name || 'Unknown'}`
    }
    
    return activity.description || 'No outcome'
  }

  function getDealInfo(opportunity: OpportunityLog) {
    const metadata = opportunity.metadata || {}
    
    // Extract contact and deal info from the nested metadata structure
    const contactName = metadata?.ai_result?.person_name || 
                       metadata?.pipedrive_result?.contact?.name || 
                       'Unknown'
    const organization = metadata?.ai_result?.organization_name || 
                        metadata?.pipedrive_result?.contact?.company_name || 
                        'Unknown'
    const dealName = metadata?.pipedrive_result?.deals?.[0]?.title || 
                    metadata?.ai_result?.deal_title || 
                    'Unknown'
    const dealValue = metadata?.ai_result?.estimated_value || 
                     metadata?.pipedrive_result?.deals?.[0]?.value || 
                     0
    const currency = metadata?.ai_result?.currency || 
                    metadata?.pipedrive_result?.deals?.[0]?.currency || 
                    'DKK'
    
    return {
      contactName,
      organization,
      dealName,
      dealValue,
      currency
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Logs</CardTitle>
          <CardDescription>Loading logs...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Opportunity Logs Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Opportunity Logs
          </CardTitle>
          <CardDescription>
            AI analysis results for email opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {opportunityLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No opportunity logs found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {opportunityLogs.map((opportunity) => {
                const status = getOpportunityStatus(opportunity)
                const dealInfo = getDealInfo(opportunity)
                
                return (
                  <div key={opportunity.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={status.color}>
                            {status.label}
                          </Badge>
                          <Badge variant="outline">
                            {(opportunity.confidence_score * 100).toFixed(1)}% confidence
                          </Badge>
                        </div>
                        
                        <h4 className="font-medium text-sm mb-1">{opportunity.subject}</h4>
                        
                        <div className="text-sm text-muted-foreground space-y-1">
                          <div className="flex items-center gap-2">
                            <User className="h-3 w-3" />
                            <span>From: {opportunity.sender_email}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Mail className="h-3 w-3" />
                            <span>To: {opportunity.recipient_email}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right text-sm text-muted-foreground">
                        {new Date(opportunity.created_at).toLocaleString()}
                      </div>
                    </div>
                    
                    {opportunity.opportunity_detected && (
                      <div className="bg-blue-50 border border-blue-200 rounded p-3 space-y-2">
                        <div className="flex items-center gap-2">
                          <Building className="h-4 w-4 text-blue-600" />
                          <span className="font-medium text-blue-900">{dealInfo.organization}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Contact:</span> {dealInfo.contactName}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Deal:</span> {dealInfo.dealName}
                          </div>
                          {dealInfo.dealValue > 0 && (
                            <div className="col-span-2">
                              <span className="text-muted-foreground">Value:</span> {dealInfo.dealValue.toLocaleString()} {dealInfo.currency}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {opportunity.reasoning && (
                      <div className="text-sm text-muted-foreground bg-gray-50 p-2 rounded">
                        <strong>AI Reasoning:</strong> {opportunity.reasoning}
                      </div>
                    )}
                  </div>
                )
              })}
              
              {/* Pagination */}
              <div className="flex items-center justify-between pt-4">
                <div className="text-sm text-muted-foreground">
                  Showing {((opportunityPage - 1) * itemsPerPage) + 1} to {Math.min(opportunityPage * itemsPerPage, opportunityTotal)} of {opportunityTotal} opportunities
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setOpportunityPage(prev => Math.max(1, prev - 1))}
                    disabled={opportunityPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setOpportunityPage(prev => prev + 1)}
                    disabled={opportunityPage * itemsPerPage >= opportunityTotal}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Activity Logs Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Activity Logs
          </CardTitle>
          <CardDescription>
            System activities and analysis outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          {activityLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No activity logs found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {activityLogs.map((activity) => {
                const status = getActivityStatus(activity.status)
                const outcome = getActivityOutcome(activity)
                
                return (
                  <div key={activity.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={status.color}>
                            {status.label}
                          </Badge>
                          <span className="text-sm font-medium capitalize">
                            {activity.activity_type.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <p className="text-sm mb-1">{outcome}</p>
                        
                        {activity.description && (
                          <p className="text-sm text-muted-foreground">{activity.description}</p>
                        )}
                      </div>
                      
                      <div className="text-right text-sm text-muted-foreground">
                        {new Date(activity.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                )
              })}
              
              {/* Pagination */}
              <div className="flex items-center justify-between pt-4">
                <div className="text-sm text-muted-foreground">
                  Showing {((activityPage - 1) * itemsPerPage) + 1} to {Math.min(activityPage * itemsPerPage, activityTotal)} of {activityTotal} activities
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActivityPage(prev => Math.max(1, prev - 1))}
                    disabled={activityPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActivityPage(prev => prev + 1)}
                    disabled={activityPage * itemsPerPage >= activityTotal}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 