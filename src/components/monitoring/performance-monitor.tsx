"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiClient } from "@/lib/api"

interface PerformanceSummary {
  period_hours: number
  total_operations: number
  successful_operations: number
  failed_operations: number
  success_rate: number
  avg_duration_ms: number
  min_duration_ms: number
  max_duration_ms: number
  operation_breakdown: Record<string, {
    total: number
    successful: number
    failed: number
    avg_duration_ms: number
    total_duration_ms: number
  }>
}

interface SystemHealth {
  health_score: number
  status: string
  cost_status: {
    daily_cost: number
    daily_limit: number
    limit_reached: boolean
    remaining_budget: number
  }
  performance_summary: PerformanceSummary
  model_stats: {
    total_models: number
    available_models: number
    default_model: string
    providers: Record<string, { total: number; available: number }>
  }
  timestamp: string
}

interface SlowestOperation {
  operation: string
  duration_ms: number
  success: boolean
  timestamp: string
  correlation_id: string
  user_id?: string
}

interface FailedOperation {
  operation: string
  duration_ms: number
  timestamp: string
  correlation_id: string
  user_id?: string
  metadata: Record<string, any>
}

export function PerformanceMonitor() {
  const [performanceSummary, setPerformanceSummary] = useState<PerformanceSummary | null>(null)
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [slowestOperations, setSlowestOperations] = useState<SlowestOperation[]>([])
  const [failedOperations, setFailedOperations] = useState<FailedOperation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPerformanceData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch performance summary
      const summaryResponse = await apiClient.getPerformanceSummary(24)
      if (summaryResponse.data) {
        setPerformanceSummary(summaryResponse.data)
      }

      // Fetch system health
      const healthResponse = await apiClient.getSystemHealth()
      if (healthResponse.data) {
        setSystemHealth(healthResponse.data)
      }

      // Fetch slowest operations
      const slowestResponse = await apiClient.getSlowestOperations(5)
      if (slowestResponse.data?.slowest_operations) {
        setSlowestOperations(slowestResponse.data.slowest_operations)
      }

      // Fetch failed operations
      const failedResponse = await apiClient.getFailedOperations(24)
      if (failedResponse.data?.failed_operations) {
        setFailedOperations(failedResponse.data.failed_operations)
      }

    } catch (err) {
      console.error("Error fetching performance data:", err)
      setError("Failed to load performance data. Please check if the backend server is running.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPerformanceData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchPerformanceData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Monitoring</CardTitle>
          <CardDescription>Loading performance data...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Monitoring</CardTitle>
          <CardDescription className="text-red-500">{error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-500"
      case "warning": return "text-yellow-500"
      case "critical": return "text-red-500"
      default: return "text-gray-500"
    }
  }

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case "healthy": return "🟢"
      case "warning": return "🟡"
      case "critical": return "🔴"
      default: return "⚪"
    }
  }

  return (
    <div className="space-y-6">
      {/* System Health Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getHealthStatusIcon(systemHealth?.status || "unknown")} System Health
            <Badge variant="outline" className={getHealthStatusColor(systemHealth?.status || "unknown")}>
              {systemHealth?.health_score || 0}/100
            </Badge>
          </CardTitle>
          <CardDescription>
            Overall system performance and health status
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{performanceSummary?.total_operations || 0}</div>
              <div className="text-xs text-muted-foreground">Total Operations</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{(performanceSummary?.success_rate || 0).toFixed(1)}%</div>
              <div className="text-xs text-muted-foreground">Success Rate</div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-2 bg-muted rounded-lg">
              <div className="text-lg font-bold">{(performanceSummary?.avg_duration_ms || 0).toFixed(0)}ms</div>
              <div className="text-xs text-muted-foreground">Avg Response</div>
            </div>
            <div className="text-center p-2 bg-muted rounded-lg">
              <div className="text-lg font-bold">{(performanceSummary?.min_duration_ms || 0).toFixed(0)}ms</div>
              <div className="text-xs text-muted-foreground">Min Response</div>
            </div>
            <div className="text-center p-2 bg-muted rounded-lg">
              <div className="text-lg font-bold">{(performanceSummary?.max_duration_ms || 0).toFixed(0)}ms</div>
              <div className="text-xs text-muted-foreground">Max Response</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="operations" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="operations">Operations</TabsTrigger>
          <TabsTrigger value="slowest">Slowest</TabsTrigger>
          <TabsTrigger value="failed">Failed</TabsTrigger>
        </TabsList>
        
        <TabsContent value="operations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Operation Breakdown</CardTitle>
              <CardDescription>Performance by operation type</CardDescription>
            </CardHeader>
            <CardContent>
              {performanceSummary?.operation_breakdown && Object.keys(performanceSummary.operation_breakdown).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(performanceSummary.operation_breakdown)
                    .sort(([,a], [,b]) => b.total - a.total)
                    .map(([operation, stats]) => (
                      <div key={operation} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{operation}</div>
                                                     <div className="text-sm text-muted-foreground">
                             {stats.successful}/{stats.total} successful • {(stats.avg_duration_ms || 0).toFixed(0)}ms avg
                           </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold">{stats.total > 0 ? ((stats.successful / stats.total) * 100).toFixed(1) : "0.0"}%</div>
                          <div className="text-xs text-muted-foreground">
                            Success Rate
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No operation data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="slowest" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Slowest Operations</CardTitle>
              <CardDescription>Operations with longest response times</CardDescription>
            </CardHeader>
            <CardContent>
              {slowestOperations.length > 0 ? (
                <div className="space-y-3">
                  {slowestOperations.map((op, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <div className="font-medium">{op.operation}</div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(op.timestamp).toLocaleString()} • {op.success ? "✅ Success" : "❌ Failed"}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{(op.duration_ms || 0).toFixed(0)}ms</div>
                        <div className="text-xs text-muted-foreground">
                          Response Time
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No slow operations found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="failed" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Failed Operations</CardTitle>
              <CardDescription>Operations that failed in the last 24 hours</CardDescription>
            </CardHeader>
            <CardContent>
              {failedOperations.length > 0 ? (
                <div className="space-y-3">
                  {failedOperations.map((op, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg border-red-200 bg-red-50">
                      <div className="flex-1">
                        <div className="font-medium text-red-800">{op.operation}</div>
                                                 <div className="text-sm text-red-600">
                           {new Date(op.timestamp).toLocaleString()} • {(op.duration_ms || 0).toFixed(0)}ms
                         </div>
                        {op.metadata?.error && (
                          <div className="text-xs text-red-500 mt-1">
                            Error: {op.metadata.error}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-red-800">❌ Failed</div>
                        <div className="text-xs text-red-600">
                          {op.duration_ms.toFixed(0)}ms
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No failed operations found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
} 