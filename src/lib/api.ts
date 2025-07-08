// API client for Railway backend communication

// Use environment variable for backend URL
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: number
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = BACKEND_URL) {
    this.baseUrl = baseUrl
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    // Try to get the session token from Supabase
    try {
      const { supabase } = await import('./supabase')
      const { data: { session } } = await supabase.auth.getSession()
      console.log('Auth session:', session ? 'Found' : 'Not found')
      if (session?.access_token) {
        console.log('Adding Authorization header with token')
        headers['Authorization'] = `Bearer ${session.access_token}`
      } else {
        console.log('No access token found in session')
      }
    } catch (error) {
      console.warn('Could not get auth token:', error)
    }

    return headers
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      const authHeaders = await this.getAuthHeaders()
      
      const response = await fetch(url, {
        headers: {
          ...authHeaders,
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      // Handle new response format: {success: true, data: ...}
      const data = result.data || result
      return { data, status: response.status }
    } catch (error) {
      console.error('API request failed:', error)
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 0,
      }
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    return this.request('/health')
  }

  // Test monitoring endpoint
  async testMonitoring(): Promise<ApiResponse> {
    return this.request('/api/monitoring/test')
  }

  // Test endpoint
  async testConnection(): Promise<ApiResponse> {
    return this.request('/api/test')
  }

  // Test POST endpoint
  async testPostConnection(): Promise<ApiResponse> {
    return this.request('/api/test', {
      method: 'POST',
    })
  }

  // Monitoring endpoints
  async getCostSummary(days: number = 7): Promise<any> {
    return this.request(`/api/monitoring/costs/summary?days=${days}`)
  }

  async getDailyCost(): Promise<any> {
    return this.request('/api/monitoring/costs/daily')
  }

  async checkDailyLimit(): Promise<any> {
    return this.request('/api/monitoring/costs/limit-check')
  }

  async getModelUsageStats(): Promise<ApiResponse> {
    return this.request('/api/monitoring/costs/model-usage')
  }

  async getPerformanceSummary(hours: number = 24): Promise<any> {
    return this.request(`/api/monitoring/performance/summary?hours=${hours}`)
  }

  async getSystemHealth(): Promise<ApiResponse> {
    return this.request('/api/monitoring/system/health')
  }

  async getRateLimitStatus(operation?: string, userId?: string): Promise<any> {
    const params = new URLSearchParams()
    if (operation) params.append('operation', operation)
    if (userId) params.append('user_id', userId)
    return this.request(`/api/monitoring/rate-limits/status?${params.toString()}`)
  }

  async getSlowestOperations(limit: number = 5): Promise<ApiResponse> {
    return this.request(`/api/monitoring/performance/slowest?limit=${limit}`)
  }

  async getFailedOperations(hours: number = 24): Promise<ApiResponse> {
    return this.request(`/api/monitoring/performance/failed?hours=${hours}`)
  }

  async getBlockedRequests(hours: number = 24): Promise<any> {
    return this.request(`/api/monitoring/rate-limits/blocked?hours=${hours}`)
  }

  async getMonitoringOverview(): Promise<any> {
    return this.request('/api/monitoring/overview')
  }
}

// Create singleton instance
export const apiClient = new ApiClient()

// Export types
export type { ApiResponse } 