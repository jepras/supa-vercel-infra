'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function LogsDashboard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Logs Dashboard</CardTitle>
        <CardDescription>Test version - logs dashboard is working</CardDescription>
      </CardHeader>
      <CardContent>
        <p>If you can see this, the logs dashboard component is working!</p>
      </CardContent>
    </Card>
  )
} 