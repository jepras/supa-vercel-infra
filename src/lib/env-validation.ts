// Environment variable validation utility

interface EnvValidationResult {
  isValid: boolean
  missing: string[]
  warnings: string[]
}

export function validateEnvironment(): EnvValidationResult {
  const requiredVars = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
    'SUPABASE_SERVICE_ROLE_KEY'
  ]

  const optionalVars = [
    'PIPEDRIVE_CLIENT_ID',
    'PIPEDRIVE_CLIENT_SECRET',
    'MICROSOFT_CLIENT_ID',
    'MICROSOFT_CLIENT_SECRET',
    'OPENAI_API_KEY',
    'ENCRYPTION_KEY',
    'WEBHOOK_SECRET'
  ]

  const missing: string[] = []
  const warnings: string[] = []

  // Check required variables
  for (const varName of requiredVars) {
    if (!process.env[varName]) {
      missing.push(varName)
    }
  }

  // Check optional variables and warn if missing
  for (const varName of optionalVars) {
    if (!process.env[varName]) {
      warnings.push(`${varName} (optional - needed for OAuth and AI features)`)
    }
  }

  // Validate Supabase URL format
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  if (supabaseUrl && !supabaseUrl.includes('supabase.co')) {
    warnings.push('NEXT_PUBLIC_SUPABASE_URL format may be incorrect')
  }

  // Validate Supabase keys format
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  if (anonKey && !anonKey.startsWith('eyJ')) {
    warnings.push('NEXT_PUBLIC_SUPABASE_ANON_KEY format may be incorrect')
  }

  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (serviceKey && !serviceKey.startsWith('eyJ')) {
    warnings.push('SUPABASE_SERVICE_ROLE_KEY format may be incorrect')
  }

  return {
    isValid: missing.length === 0,
    missing,
    warnings
  }
}

export function logEnvironmentStatus(): void {
  const result = validateEnvironment()
  
  console.log('🔧 Environment Configuration Status:')
  console.log('=====================================')
  
  if (result.isValid) {
    console.log('✅ All required environment variables are set!')
  } else {
    console.log('❌ Missing required environment variables:')
    result.missing.forEach(varName => {
      console.log(`   - ${varName}`)
    })
  }

  if (result.warnings.length > 0) {
    console.log('\n⚠️  Warnings:')
    result.warnings.forEach(warning => {
      console.log(`   - ${warning}`)
    })
  }

  // Show current environment
  console.log(`\n🌍 Environment: Production`)
  console.log(`🚀 Vercel URL: ${process.env.VERCEL_URL || 'Not deployed'}`)
  
  if (process.env.NEXT_PUBLIC_SUPABASE_URL) {
    console.log(`🔗 Supabase URL: ${process.env.NEXT_PUBLIC_SUPABASE_URL}`)
  }
} 