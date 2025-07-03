// API client for Railway backend communication

// Automatically determine backend URL based on environment
const getBackendUrl = () => {
  // In development, use localhost
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000'
  }
  
  // In production, use Railway URL
  return process.env.NEXT_PUBLIC_BACKEND_URL || 'https://supa-vercel-infra-production.up.railway.app'
}

const BACKEND_URL = getBackendUrl()

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

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
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
}

// Create singleton instance
export const apiClient = new ApiClient()

// Export types
export type { ApiResponse } 