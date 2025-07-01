import { NextRequest, NextResponse } from 'next/server'
import { validateEnvironment } from '@/lib/env-validation'

export async function GET(request: NextRequest) {
  try {
    const envStatus = validateEnvironment()
    
    // Don't expose sensitive data in production
    const isProduction = process.env.NODE_ENV === 'production'
    
    const response = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      vercelUrl: process.env.VERCEL_URL || null,
      envValidation: {
        isValid: envStatus.isValid,
        missingCount: envStatus.missing.length,
        warningCount: envStatus.warnings.length,
        // Only show missing vars in production, not the actual names
        hasMissingVars: envStatus.missing.length > 0,
        hasWarnings: envStatus.warnings.length > 0
      },
      // Only show detailed info in development
      details: isProduction ? null : {
        missing: envStatus.missing,
        warnings: envStatus.warnings,
        supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'Set' : 'Missing',
        hasAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        hasServiceKey: !!process.env.SUPABASE_SERVICE_ROLE_KEY
      }
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