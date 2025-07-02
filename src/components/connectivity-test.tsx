'use client'

import { useState } from 'react'
import { apiClient, ApiResponse } from '../lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface TestResult {
  endpoint: string
  method: string
  response: ApiResponse
  timestamp: string
}

export function ConnectivityTest() {
  const [results, setResults] = useState<TestResult[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const runTest = async (endpoint: string, method: 'GET' | 'POST') => {
    setIsLoading(true)
    const timestamp = new Date().toISOString()
    
    let response: ApiResponse
    if (method === 'GET') {
      response = await apiClient.testConnection()
    } else {
      response = await apiClient.testPostConnection()
    }

    const result: TestResult = {
      endpoint,
      method,
      response,
      timestamp,
    }

    setResults(prev => [result, ...prev])
    setIsLoading(false)
  }

  const runHealthCheck = async () => {
    setIsLoading(true)
    const timestamp = new Date().toISOString()
    const response = await apiClient.healthCheck()
    
    const result: TestResult = {
      endpoint: '/health',
      method: 'GET',
      response,
      timestamp,
    }

    setResults(prev => [result, ...prev])
    setIsLoading(false)
  }

  const clearResults = () => {
    setResults([])
  }

  const getStatusColor = (status: number) => {
    if (status === 0) return 'destructive'
    if (status >= 200 && status < 300) return 'default'
    return 'secondary'
  }

  const getStatusText = (status: number) => {
    if (status === 0) return 'Failed'
    if (status >= 200 && status < 300) return 'Success'
    return `Error ${status}`
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Backend Connectivity Test</CardTitle>
        <CardDescription>
          Test the connection between frontend and Railway backend
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Test Controls */}
        <div className="flex flex-wrap gap-2">
          <Button 
            onClick={runHealthCheck} 
            disabled={isLoading}
            variant="outline"
          >
            Health Check
          </Button>
          <Button 
            onClick={() => runTest('/api/test', 'GET')} 
            disabled={isLoading}
            variant="outline"
          >
            Test GET
          </Button>
          <Button 
            onClick={() => runTest('/api/test', 'POST')} 
            disabled={isLoading}
            variant="outline"
          >
            Test POST
          </Button>
          <Button 
            onClick={clearResults} 
            disabled={isLoading}
            variant="destructive"
          >
            Clear Results
          </Button>
        </div>

        {/* Results */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">Test Results</h3>
          {results.length === 0 && (
            <p className="text-muted-foreground">No tests run yet. Click a button above to start testing.</p>
          )}
          {results.map((result, index) => (
            <Card key={index} className="border-l-4 border-l-blue-500">
              <CardContent className="pt-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm">
                      {result.method} {result.endpoint}
                    </span>
                    <Badge variant={getStatusColor(result.response.status)}>
                      {getStatusText(result.response.status)}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(result.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                {result.response.error ? (
                  <div className="text-red-600 text-sm">
                    <strong>Error:</strong> {result.response.error}
                  </div>
                ) : (
                  <pre className="text-xs bg-muted p-2 rounded overflow-auto">
                    {JSON.stringify(result.response.data, null, 2)}
                  </pre>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Environment Info */}
        <Card className="bg-muted/50">
          <CardContent className="pt-4">
            <h4 className="font-semibold mb-2">Environment Information</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="font-medium">Backend URL:</span>
                <span className="ml-2 font-mono">
                  {process.env.NODE_ENV === 'development' 
                    ? 'http://localhost:8000' 
                    : (process.env.NEXT_PUBLIC_BACKEND_URL || 'https://supa-vercel-infra-production.up.railway.app')
                  }
                </span>
              </div>
              <div>
                <span className="font-medium">Environment:</span>
                <span className="ml-2">{process.env.NODE_ENV}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  )
} 