import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  return NextResponse.json({
    message: 'Hello from Next.js API route!',
    timestamp: new Date().toISOString(),
    status: 'working'
  })
}

export async function POST(request: NextRequest) {
  return NextResponse.json({
    message: 'POST request received from Next.js API route!',
    timestamp: new Date().toISOString(),
    status: 'working'
  })
} 