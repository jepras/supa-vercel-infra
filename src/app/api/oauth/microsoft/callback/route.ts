import { NextRequest, NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    console.log('Frontend Microsoft API route - GET request received')
    
    // Get query parameters for OAuth callback
    const { searchParams } = new URL(request.url)
    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const error = searchParams.get('error')
    
    console.log('Frontend Microsoft API route - Query params:', { code, state, error })
    
    if (error) {
      return NextResponse.json(
        { error: `OAuth error: ${error}` },
        { status: 400 }
      )
    }
    
    if (!code) {
      return NextResponse.json(
        { error: 'Authorization code not provided' },
        { status: 400 }
      )
    }
    
    // Get the Supabase session from the request
    const supabase = createServerSupabaseClient()
    const authHeader = request.headers.get('authorization')
    
    console.log('Frontend Microsoft API route - Auth header present:', !!authHeader)
    
    // Prepare headers for backend request
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    
    // Add Authorization header if we have one
    if (authHeader) {
      headers['Authorization'] = authHeader
      console.log('Frontend Microsoft API route - Forwarding Authorization header')
    } else {
      console.log('Frontend Microsoft API route - No Authorization header found')
    }
    
    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/api/oauth/microsoft/callback`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ code, state }),
    })

    console.log('Frontend Microsoft API route - Backend response status:', response.status)

    const data = await response.json()
    console.log('Frontend Microsoft API route - Backend response data:', data)

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || 'OAuth callback failed' },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Microsoft OAuth callback error:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    console.log('Frontend Microsoft API route - Backend URL:', BACKEND_URL)
    console.log('Frontend Microsoft API route - Request body:', body)
    
    // Get the Supabase session from the request
    const supabase = createServerSupabaseClient()
    const authHeader = request.headers.get('authorization')
    
    console.log('Frontend Microsoft API route - Auth header present:', !!authHeader)
    
    // Prepare headers for backend request
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    
    // Add Authorization header if we have one
    if (authHeader) {
      headers['Authorization'] = authHeader
      console.log('Frontend Microsoft API route - Forwarding Authorization header')
    } else {
      console.log('Frontend Microsoft API route - No Authorization header found')
    }
    
    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/api/oauth/microsoft/callback`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    })

    console.log('Frontend Microsoft API route - Backend response status:', response.status)

    const data = await response.json()
    console.log('Frontend Microsoft API route - Backend response data:', data)

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || 'OAuth callback failed' },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Microsoft OAuth callback error:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
} 