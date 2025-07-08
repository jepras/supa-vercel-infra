"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useMonitoring } from './monitoring-context'

export function RateLimitMonitor() {
  const { data, loading, error } = useMonitoring()
  const rateLimitStatus = data?.rateLimitStatus
  const blockedRequests = data?.blockedRequests

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

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Rate Limit Monitoring</CardTitle>
          <CardDescription>API rate limit status and blocked requests</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {rateLimitStatus && Object.keys(rateLimitStatus).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(rateLimitStatus).map(([operation, status]: [string, any]) => (
                <div key={operation} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="font-medium">{operation}</div>
                  <div className="text-xs text-muted-foreground">
                    {status.requests_in_window} / {status.max_requests} in {status.window_seconds}s
                  </div>
                  <div className="font-bold">
                    {status.remaining_requests} left
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
      <Card>
        <CardHeader>
          <CardTitle>Blocked Requests</CardTitle>
          <CardDescription>Recent blocked API requests</CardDescription>
        </CardHeader>
        <CardContent>
          {blockedRequests && blockedRequests.length > 0 ? (
            <div className="space-y-3">
              {blockedRequests.map((req: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="font-medium">{req.operation}</div>
                  <div className="text-red-500 font-bold">Blocked</div>
                  <div className="text-xs text-muted-foreground">{new Date(req.timestamp).toLocaleString()}</div>
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
    </div>
  )
} 