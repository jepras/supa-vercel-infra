'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiClient } from '@/lib/api'

interface MonitoringData {
  costSummary: any
  dailyCost: any
  limitCheck: any
  modelStats: any
  performanceSummary: any
  slowestOperations: any
  failedOperations: any
  rateLimitStatus: any
  blockedRequests: any
  systemHealth: any
}

interface MonitoringContextType {
  data: MonitoringData | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

const MonitoringContext = createContext<MonitoringContextType | undefined>(undefined)

export function MonitoringProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<MonitoringData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAllMonitoringData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all monitoring data in parallel
      const [
        costSummaryResponse,
        dailyCostResponse,
        limitCheckResponse,
        modelStatsResponse,
        performanceSummaryResponse,
        slowestOperationsResponse,
        failedOperationsResponse,
        rateLimitStatusResponse,
        blockedRequestsResponse,
        systemHealthResponse,
      ] = await Promise.all([
        apiClient.getCostSummary(7),
        apiClient.getDailyCost(),
        apiClient.checkDailyLimit(),
        apiClient.getModelUsageStats(),
        apiClient.getPerformanceSummary(24),
        apiClient.getSlowestOperations(5),
        apiClient.getFailedOperations(24),
        apiClient.getRateLimitStatus(),
        apiClient.getBlockedRequests(24),
        apiClient.getSystemHealth(),
      ])

      setData({
        costSummary: costSummaryResponse.data,
        dailyCost: dailyCostResponse.data,
        limitCheck: limitCheckResponse.data,
        modelStats: modelStatsResponse.data,
        performanceSummary: performanceSummaryResponse.data,
        slowestOperations: slowestOperationsResponse.data,
        failedOperations: failedOperationsResponse.data,
        rateLimitStatus: rateLimitStatusResponse.data,
        blockedRequests: blockedRequestsResponse.data,
        systemHealth: systemHealthResponse.data,
      })
    } catch (err) {
      console.error('Error fetching monitoring data:', err)
      setError('Failed to load monitoring data. Please check if the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllMonitoringData()
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchAllMonitoringData, 300000)
    return () => clearInterval(interval)
  }, [])

  const refresh = async () => {
    await fetchAllMonitoringData()
  }

  return (
    <MonitoringContext.Provider value={{ data, loading, error, refresh }}>
      {children}
    </MonitoringContext.Provider>
  )
}

export function useMonitoring() {
  const context = useContext(MonitoringContext)
  if (context === undefined) {
    throw new Error('useMonitoring must be used within a MonitoringProvider')
  }
  return context
} 