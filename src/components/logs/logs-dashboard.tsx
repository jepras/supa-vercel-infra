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
  const { user } = useAuth()
  const [opportunityLogs, setOpportunityLogs] = useState<OpportunityLog[]>([])
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([])
  const [loading, setLoading] = useState(true)
  const [opportunityPage, setOpportunityPage] = useState(1)
  const [activityPage, setActivityPage] = useState(1)
  const [opportunityTotal, setOpportunityTotal] = useState(0)
  const [activityTotal, setActivityTotal] = useState(0)
  const itemsPerPage = 15 // Increased from 10 to show more items

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
      return { label: 'Opportunity Detected', color: 'bg-green-950/50 text-green-400 border border-green-800' }
    }
    return { label: 'No Opportunity', color: 'bg-muted text-muted-foreground border border-border' }
  }

  function getActivityStatus(status: string) {
    switch (status) {
      case 'success':
        return { label: 'Success', color: 'bg-green-950/50 text-green-400 border border-green-800' }
      case 'error':
        return { label: 'Error', color: 'bg-red-950/50 text-red-400 border border-red-800' }
      case 'warning':
        return { label: 'Warning', color: 'bg-yellow-950/50 text-yellow-400 border border-yellow-800' }
      default:
        return { label: 'Pending', color: 'bg-blue-950/50 text-blue-400 border border-blue-800' }
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
    <div className="space-y-4">
      {/* Opportunity Logs Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <DollarSign className="h-4 w-4" />
            Opportunity Logs
          </CardTitle>
          <CardDescription>
            AI analysis results for email opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {opportunityLogs.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              <Mail className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No opportunity logs found</p>
            </div>
          ) : (
            <div className="space-y-2">
              {opportunityLogs.map((opportunity) => {
                const status = getOpportunityStatus(opportunity)
                const dealInfo = getDealInfo(opportunity)
                
                return (
                  <div key={opportunity.id} className="border rounded-md p-3 space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={`${status.color} text-xs`}>
                            {status.label}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {(opportunity.confidence_score * 100).toFixed(1)}% confidence
                          </Badge>
                        </div>
                        
                        <h4 className="font-medium text-sm mb-1 truncate">{opportunity.subject}</h4>
                        
                        <div className="text-xs text-muted-foreground space-y-0.5">
                          <div className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            <span className="truncate">From: {opportunity.sender_email}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            <span className="truncate">To: {opportunity.recipient_email}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right text-xs text-muted-foreground ml-2 flex-shrink-0">
                        {new Date(opportunity.created_at).toLocaleString()}
                      </div>
                    </div>
                    
                    {opportunity.opportunity_detected && (
                      <div className="bg-blue-950/50 border border-blue-800/50 rounded p-2 space-y-1">
                        <div className="flex items-center gap-1">
                          <Building className="h-3 w-3 text-blue-400" />
                          <span className="font-medium text-blue-300 text-xs">{dealInfo.organization}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
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
                      <div className="text-xs text-muted-foreground bg-muted p-2 rounded border border-border">
                        <strong>AI Reasoning:</strong> {opportunity.reasoning}
                      </div>
                    )}
                  </div>
                )
              })}
              
              {/* Pagination */}
              <div className="flex items-center justify-between pt-3">
                <div className="text-xs text-muted-foreground">
                  Showing {((opportunityPage - 1) * itemsPerPage) + 1} to {Math.min(opportunityPage * itemsPerPage, opportunityTotal)} of {opportunityTotal} opportunities
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setOpportunityPage(prev => Math.max(1, prev - 1))}
                    disabled={opportunityPage === 1}
                  >
                    <ChevronLeft className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setOpportunityPage(prev => prev + 1)}
                    disabled={opportunityPage * itemsPerPage >= opportunityTotal}
                  >
                    <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Activity Logs Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-4 w-4" />
            Activity Logs
          </CardTitle>
          <CardDescription>
            System activities and analysis outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          {activityLogs.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No activity logs found</p>
            </div>
          ) : (
            <div className="space-y-2">
              {activityLogs.map((activity) => {
                const status = getActivityStatus(activity.status)
                const outcome = getActivityOutcome(activity)
                
                return (
                  <div key={activity.id} className="border rounded-md p-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={`${status.color} text-xs`}>
                            {status.label}
                          </Badge>
                          <span className="text-xs font-medium capitalize">
                            {activity.activity_type.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <p className="text-xs mb-1">{outcome}</p>
                        
                        {activity.description && (
                          <p className="text-xs text-muted-foreground">{activity.description}</p>
                        )}
                      </div>
                      
                      <div className="text-right text-xs text-muted-foreground ml-2 flex-shrink-0">
                        {new Date(activity.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                )
              })}
              
              {/* Pagination */}
              <div className="flex items-center justify-between pt-3">
                <div className="text-xs text-muted-foreground">
                  Showing {((activityPage - 1) * itemsPerPage) + 1} to {Math.min(activityPage * itemsPerPage, activityTotal)} of {activityTotal} activities
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActivityPage(prev => Math.max(1, prev - 1))}
                    disabled={activityPage === 1}
                  >
                    <ChevronLeft className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActivityPage(prev => prev + 1)}
                    disabled={activityPage * itemsPerPage >= activityTotal}
                  >
                    <ChevronRight className="h-3 w-3" />
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