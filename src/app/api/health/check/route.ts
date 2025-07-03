import { NextRequest, NextResponse } from 'next/server'
import { validateEnvironment } from '@/lib/env-validation'

export async function GET(request: NextRequest) {
  try {
    const envStatus = validateEnvironment()
    
    const response = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      environment: 'production',
      vercelUrl: process.env.VERCEL_URL || null,
      envValidation: {
        isValid: envStatus.isValid,
        missingCount: envStatus.missing.length,
        warningCount: envStatus.warnings.length,
        // Only show missing vars in production, not the actual names
        hasMissingVars: envStatus.missing.length > 0,
        hasWarnings: envStatus.warnings.length > 0
      },
      // Don't expose sensitive data in production
      details: null
    }

    return NextResponse.json(response, {
      status: envStatus.isValid ? 200 : 500
    })
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Health check failed',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
} 