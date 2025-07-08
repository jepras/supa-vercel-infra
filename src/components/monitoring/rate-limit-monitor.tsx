"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiClient } from "@/lib/api"

interface RateLimitStatus {
  operation: string
  current_usage: number
  limit: number
  reset_time: string
  time_window_seconds: number
  is_blocked: boolean
  remaining_requests: number
  usage_percentage: number
}

interface RateLimitSummary {
  total_operations: number
  blocked_operations: number
  near_limit_operations: number
  operations: RateLimitStatus[]
}

interface BlockedRequest {
  operation: string
  user_id?: string
  timestamp: string
  ip_address?: string
  user_agent?: string
  correlation_id: string
}

export function RateLimitMonitor() {
  const [rateLimitSummary, setRateLimitSummary] = useState<RateLimitSummary | null>(null)
  const [blockedRequests, setBlockedRequests] = useState<BlockedRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchRateLimitData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch rate limit status for all operations
      const statusResponse = await apiClient.getRateLimitStatus()
      if (statusResponse.data) {
        setRateLimitSummary(statusResponse.data)
      }

      // Fetch blocked requests
      const blockedResponse = await apiClient.getBlockedRequests(24)
      if (blockedResponse.data?.blocked_requests) {
        setBlockedRequests(blockedResponse.data.blocked_requests)
      }

    } catch (err) {
      console.error("Error fetching rate limit data:", err)
      setError("Failed to load rate limit data. Please check if the backend server is running.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRateLimitData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchRateLimitData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Rate Limit Monitoring</CardTitle>
          <CardDescription>Loading rate limit data...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Rate Limit Monitoring</CardTitle>
          <CardDescription className="text-red-500">{error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const getUsageStatusColor = (percentage: number) => {
    if (percentage >= 90) return "text-red-500"
    if (percentage >= 75) return "text-yellow-500"
    return "text-green-500"
  }

  const getUsageStatusIcon = (percentage: number) => {
    if (percentage >= 90) return "🔴"
    if (percentage >= 75) return "🟡"
    return "🟢"
  }

  return (
    <div className="space-y-6">
      {/* Rate Limit Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🚦 Rate Limit Monitoring
            <Badge variant="outline" className="text-orange-500">
              {rateLimitSummary?.blocked_operations || 0} Blocked
            </Badge>
          </CardTitle>
          <CardDescription>
            API rate limiting and usage tracking
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{rateLimitSummary?.total_operations || 0}</div>
              <div className="text-xs text-muted-foreground">Total Operations</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold text-red-500">{rateLimitSummary?.blocked_operations || 0}</div>
              <div className="text-xs text-muted-foreground">Blocked Operations</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold text-yellow-500">{rateLimitSummary?.near_limit_operations || 0}</div>
              <div className="text-xs text-muted-foreground">Near Limit</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="status" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="status">Rate Limits</TabsTrigger>
          <TabsTrigger value="blocked">Blocked Requests</TabsTrigger>
        </TabsList>
        
        <TabsContent value="status" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Rate Limit Status</CardTitle>
              <CardDescription>Current usage for each operation</CardDescription>
            </CardHeader>
            <CardContent>
              {rateLimitSummary?.operations && rateLimitSummary.operations.length > 0 ? (
                <div className="space-y-3">
                  {rateLimitSummary.operations
                    .sort((a, b) => b.usage_percentage - a.usage_percentage)
                    .map((operation) => (
                      <div key={operation.operation} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium flex items-center gap-2">
                            {getUsageStatusIcon(operation.usage_percentage)} {operation.operation}
                            {operation.is_blocked && (
                              <Badge variant="destructive" className="text-xs">BLOCKED</Badge>
                            )}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {operation.current_usage}/{operation.limit} requests • 
                            Resets {new Date(operation.reset_time).toLocaleTimeString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-bold ${getUsageStatusColor(operation.usage_percentage)}`}>
                            {operation.usage_percentage.toFixed(1)}%
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {operation.remaining_requests} remaining
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No rate limit data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="blocked" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Blocked Requests</CardTitle>
              <CardDescription>Requests blocked by rate limits in the last 24 hours</CardDescription>
            </CardHeader>
            <CardContent>
              {blockedRequests.length > 0 ? (
                <div className="space-y-3">
                  {blockedRequests.map((request, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg border-red-200 bg-red-50">
                      <div className="flex-1">
                        <div className="font-medium text-red-800">{request.operation}</div>
                        <div className="text-sm text-red-600">
                          {new Date(request.timestamp).toLocaleString()}
                          {request.user_id && ` • User: ${request.user_id}`}
                        </div>
                        {request.ip_address && (
                          <div className="text-xs text-red-500 mt-1">
                            IP: {request.ip_address}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-red-800">🚫 Blocked</div>
                        <div className="text-xs text-red-600">
                          Rate Limit
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No blocked requests found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
} 