"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiClient } from "@/lib/api"

interface CostSummary {
  total_cost: number
  total_calls: number
  daily_costs: Record<string, number>
  model_costs: Record<string, number>
  period_days: number
}

interface DailyCost {
  daily_cost: number
  limit_check: {
    daily_cost: number
    daily_limit: number
    limit_reached: boolean
    remaining_budget: number
  }
}

interface ModelUsageStats {
  [model: string]: {
    total_calls: number
    total_cost: number
    total_input_tokens: number
    total_output_tokens: number
  }
}

export function CostMonitor() {
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null)
  const [dailyCost, setDailyCost] = useState<DailyCost | null>(null)
  const [modelStats, setModelStats] = useState<ModelUsageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCostData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch cost summary (7 days)
      const summaryResponse = await apiClient.getCostSummary(7)
      if (summaryResponse.data) {
        setCostSummary(summaryResponse.data)
      }

      // Fetch daily cost
      const dailyResponse = await apiClient.getDailyCost()
      if (dailyResponse.data) {
        setDailyCost(dailyResponse.data)
      }

      // Fetch model usage stats
      const modelResponse = await apiClient.getModelUsageStats()
      if (modelResponse.data) {
        setModelStats(modelResponse.data)
      }

    } catch (err) {
      console.error("Error fetching cost data:", err)
      setError("Failed to load cost data. Please check if the backend server is running.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCostData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchCostData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Cost Monitoring</CardTitle>
          <CardDescription>Loading cost data...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Cost Monitoring</CardTitle>
          <CardDescription className="text-red-500">{error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const dailyLimitPercentage = dailyCost 
    ? (dailyCost.limit_check.daily_cost / dailyCost.limit_check.daily_limit) * 100 
    : 0

  const getLimitStatusColor = () => {
    if (dailyLimitPercentage >= 90) return "text-red-500"
    if (dailyLimitPercentage >= 75) return "text-yellow-500"
    return "text-green-500"
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            💰 Cost Monitoring
            <Badge variant="outline" className={getLimitStatusColor()}>
              ${dailyCost?.limit_check.daily_cost.toFixed(4) || "0.0000"}
            </Badge>
          </CardTitle>
          <CardDescription>
            OpenRouter API usage and cost tracking
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Daily Limit Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Daily Budget Usage</span>
              <span className={getLimitStatusColor()}>
                ${dailyCost?.limit_check.daily_cost.toFixed(4) || "0.0000"} / ${dailyCost?.limit_check.daily_limit.toFixed(2) || "20.00"}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(dailyLimitPercentage, 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Remaining: ${dailyCost?.limit_check.remaining_budget.toFixed(2) || "20.00"}</span>
              <span>{dailyLimitPercentage.toFixed(1)}% used</span>
            </div>
          </div>

          {/* 7-Day Summary */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold">${(costSummary?.total_cost || 0).toFixed(4)}</div>
              <div className="text-xs text-muted-foreground">7-Day Total</div>
            </div>
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{costSummary?.total_calls || 0}</div>
              <div className="text-xs text-muted-foreground">Total Calls</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="models" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="models">Model Usage</TabsTrigger>
          <TabsTrigger value="daily">Daily Trends</TabsTrigger>
        </TabsList>
        
        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Model Usage Statistics</CardTitle>
              <CardDescription>Cost breakdown by AI model</CardDescription>
            </CardHeader>
            <CardContent>
              {modelStats && Object.keys(modelStats).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(modelStats)
                    .sort(([,a], [,b]) => b.total_cost - a.total_cost)
                    .map(([model, stats]) => (
                      <div key={model} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{model}</div>
                          <div className="text-sm text-muted-foreground">
                            {stats.total_calls} calls • {stats.total_input_tokens.toLocaleString()} input • {stats.total_output_tokens.toLocaleString()} output tokens
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold">${(stats.total_cost || 0).toFixed(4)}</div>
                          <div className="text-xs text-muted-foreground">
                            ${stats.total_calls > 0 ? ((stats.total_cost || 0) / stats.total_calls).toFixed(6) : "0.000000"}/call
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No model usage data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="daily" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Daily Cost Trends</CardTitle>
              <CardDescription>7-day cost history</CardDescription>
            </CardHeader>
            <CardContent>
              {costSummary?.daily_costs && Object.keys(costSummary.daily_costs).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(costSummary.daily_costs)
                    .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
                    .map(([date, cost]) => (
                      <div key={date} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="font-medium">
                          {new Date(date).toLocaleDateString('en-US', { 
                            weekday: 'short', 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </div>
                        <div className="font-bold">${(cost || 0).toFixed(4)}</div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No daily cost data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
} 