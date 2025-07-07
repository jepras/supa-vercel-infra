# Project Implementation Tasks

## Overview
This document breaks down the Next.js Frontend + Railway Python Backend SaaS application into implementable tasks with clear verification criteria and manual intervention requirements.

## Phase 1: Project Foundation & Setup

### 1.1 Project Structure Setup
**Priority**: Critical | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Create Next.js project with TypeScript and Tailwind CSS (latest version)
- [x] Set up project directory structure (src/, backend/, supabase/, etc.)
- [x] Initialize Git repository
- [x] Create initial package.json with required dependencies
- [x] Set up Tailwind CSS configuration
- [x] Create basic Next.js configuration

#### Verification:
- [x] `npm run dev` starts successfully
- [x] Project structure matches specification
- [x] TypeScript compilation works
- [x] Tailwind CSS is working

### 1.2 Railway Backend Setup
**Priority**: Critical | **Manual Intervention**: Required | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Create FastAPI backend structure in backend/ directory
- [x] Set up FastAPI application with basic health endpoint
- [x] Create Dockerfile for Railway deployment
- [x] Configure requirements.txt with FastAPI dependencies
- [x] Set up .dockerignore file
- [x] Test Docker build locally
- [x] Deploy to Railway for testing

#### Manual Intervention Required:
- [x] Create Railway account and project
- [x] Configure Railway environment variables
- [x] Set root directory to `backend` in Railway

#### Verification:
- [x] FastAPI app starts locally with uvicorn
- [x] Docker image builds successfully
- [x] Railway deployment is live and accessible
- [x] Health endpoint responds correctly
- [x] Environment variables are properly configured

### 1.3 Supabase Database Setup with Migrations
**Priority**: Critical | **Manual Intervention**: Required | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Create Supabase project (manual)
- [x] Install and configure Supabase CLI
- [x] Create initial migration files for database schema
- [x] Set up database schema (tables: integrations, opportunity_logs, activity_logs)
- [x] Configure Row Level Security (RLS) policies
- [x] Add performance indexes for queries
- [x] Test database connections
- [x] Create migration workflow

#### Manual Intervention Required:
- [x] Create Supabase account and project via dashboard
- [x] Copy Supabase URL and keys for environment variables

#### Verification:
- [x] Database tables exist with correct schema
- [x] RLS policies are active and working
- [x] Can connect to database from both frontend and backend
- [x] Test data can be inserted and retrieved
- [x] Migrations can be applied and rolled back
- [x] Performance indexes are created

### 1.4 Environment Configuration
**Priority**: Critical | **Manual Intervention**: Required | **Estimated Time**: 30 minutes

#### Tasks:
- [x] Create .env.local file for local development
- [x] Set up Vercel environment variables for frontend
- [x] Set up Railway environment variables for backend
- [x] Configure environment variable validation
- [x] Create .vercelignore to exclude backend from frontend deployment

#### Manual Intervention Required:
- [x] Obtain Supabase credentials
- [x] Set up Vercel project and configure environment variables
- [x] Set up Railway project and configure environment variables
- [x] Update Supabase Auth redirect URLs for production

#### Verification:
- [x] Environment variables are accessible in both frontend and backend
- [x] No sensitive data is exposed in client-side code
- [x] Vercel deployment can access all required variables
- [x] Railway deployment can access all required variables
- [x] Both deployments complete successfully without errors
- [x] Production redirect URLs work correctly for authentication

## Phase 2: Authentication & User Management

### 2.1 Supabase Authentication Setup
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Install and configure Supabase client
- [x] Create authentication context and hooks
- [x] Implement login/signup pages
- [x] Set up protected routes
- [x] Create user profile management

#### Verification:
- [x] Users can register and login
- [x] Protected routes redirect unauthenticated users
- [x] User session persists across page reloads
- [x] Logout functionality works

### 2.2 Authentication UI Components
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Install and configure Shadcn/ui
- [x] Create login form with validation
- [x] Create signup form with validation
- [x] Implement password reset functionality
- [x] Create user profile component

#### Verification:
- [x] UI is responsive and accessible
- [x] Forms have proper validation and error handling
- [x] Form submissions work correctly
- [x] Error messages are user-friendly

## Phase 3: OAuth Integration Framework

### 3.0 Frontend-Backend Connectivity Test
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 1 hour

#### Tasks:
- [x] Create simple API endpoint in backend for testing
- [x] Create frontend component to test backend connection
- [x] Implement error handling for connection failures
- [x] Test with both local and production backend URLs
- [x] Verify CORS configuration is working
- [x] Implement dynamic backend URL selection (localhost for dev, Railway for prod)
- [x] Fix CORS configuration for production domains

#### Manual Intervention Required:
- [x] Set FRONTEND_URL environment variable in Railway backend to Vercel domain

#### Verification:
- [x] Frontend can successfully call backend API
- [x] Error handling works when backend is unavailable
- [x] CORS allows frontend to access backend
- [x] Connection works in both development and production
- [x] Response times are acceptable
- [x] Build cache issues resolved with fresh deployment

### 3.1 OAuth Manager Implementation
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 3-4 hours

#### Tasks:
- [x] Create OAuth manager utility functions in backend
- [x] Implement token encryption/decryption
- [x] Create OAuth flow handlers for Pipedrive and Outlook
- [x] Set up token refresh logic
- [x] Implement connection status checking

#### Manual Intervention Required:
- [x] Register applications with Pipedrive Developer Hub
- [x] Register applications with Microsoft Azure AD
- [x] Configure redirect URIs for OAuth callbacks (Railway URLs)

#### Verification:
- [x] OAuth flows can be initiated
- [x] Tokens are properly encrypted and stored
- [x] Token refresh works automatically
- [x] Connection status can be verified

### 3.1.1 OAuth Infrastructure Setup (COMPLETED)
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 2 hours

#### Tasks:
- [x] Create OAuth manager utility (`backend/app/lib/oauth_manager.py`)
- [x] Implement token encryption/decryption (`backend/app/lib/encryption.py`)
- [x] Create Supabase client utility (`backend/app/lib/supabase_client.py`)
- [x] Add test endpoint for OAuth infrastructure (`/api/oauth/test`)
- [x] Handle base64-encoded encryption keys
- [x] Set up proper error handling and logging

#### Manual Intervention Required:
- [x] Generate 32-byte base64 encryption key
- [x] Set ENCRYPTION_KEY environment variable in Railway
- [x] Push feature branch to GitHub for Railway deployment

#### Verification:
- [x] Backend starts without encryption errors
- [x] OAuth manager can generate authorization URLs
- [x] Token encryption/decryption works correctly
- [x] Supabase client can connect to database
- [x] Test endpoint returns success response
- [x] Railway deployment works with feature branch

### 3.2 OAuth Provider Setup
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Configure Pipedrive OAuth application
- [x] Configure Microsoft Outlook OAuth application
- [x] Set up webhook endpoints for Outlook (Phase 5.2)
- [x] Test OAuth flows end-to-end

#### Manual Intervention Required:
- [x] Create Pipedrive app in Developer Hub
- [x] Create Azure AD app registration
- [x] Configure app permissions and scopes
- [x] Set up webhook subscriptions in Microsoft Graph (Phase 5.2)

#### Verification:
- [x] OAuth flows complete successfully
- [x] Access tokens are obtained and stored
- [x] Webhook subscriptions are created (Phase 5.2)
- [x] API calls to providers work

## Phase 4: Frontend Dashboard & UI

### 4.1 Dashboard Layout & Navigation
**Priority**: Medium | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Create main dashboard layout
- [ ] Implement navigation sidebar/menu
- [x] Create responsive design
- [ ] Set up routing structure
- [ ] Implement breadcrumbs

#### Verification:
- [x] Dashboard loads correctly
- [x] Navigation works on all screen sizes
- [ ] Routes are properly configured
- [x] Layout is consistent across pages

### 4.2 Integration Management UI
**Priority**: Medium | **Manual Intervention**: None | **Estimated Time**: 3-4 hours

#### Tasks:
- [x] Create integration cards for Pipedrive and Outlook
- [x] Implement connection/disconnection flows
- [x] Create integration status indicators
- [x] Add automation toggle switches
- [ ] Implement integration settings

#### Verification:
- [x] Integration cards display correct status
- [x] Connect/disconnect buttons work
- [x] Status updates in real-time
- [ ] Settings can be modified

### 4.3 Real-time Activity Logs & Monitoring
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 3-4 hours

#### Tasks:
- [ ] Create real-time subscription hooks
- [ ] Implement activity logs table with live updates
- [ ] Create log filtering and search
- [ ] Add real-time opportunity detection logs
- [ ] Implement log export functionality
- [ ] Add loading states for real-time data

#### Verification:
- [ ] Logs display correctly
- [ ] Real-time updates work without page refresh
- [ ] Filtering and search work
- [ ] Live updates function properly
- [ ] Export functionality works

## Phase 5: Webhooks & AI Processing

### 5.1 Database Schema for Email Processing
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 30 minutes

#### Tasks:
- [x] Create `emails` table in Supabase for storing email metadata
- [x] Create `webhook_subscriptions` table for managing Microsoft Graph subscriptions
- [x] Add RLS policies for email data access
- [x] Create indexes for email processing queries
- [x] Add migration files for new schema


#### Verification:
- [x] Database tables are created successfully
- [x] RLS policies work correctly
- [x] Indexes improve query performance
- [x] Migrations can be applied and rolled back

### 5.2 Webhook Implementation (Outlook First)
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 3-4 hours

#### Phase 1: Local Development Setup
- [ ] Install and configure ngrok for local webhook testing
- [ ] Create webhook endpoint in existing Railway backend (`/api/webhooks/microsoft/email`)
- [ ] Implement webhook validation and security (Microsoft Graph validation)
- [ ] Add basic webhook logging and error handling
- [ ] Test webhook reception locally with ngrok

#### Phase 2: Microsoft Graph Webhook Subscription
- [ ] Create webhook subscription endpoint (`/api/webhooks/microsoft/subscribe`)
- [ ] Implement subscription creation with Microsoft Graph API
- [ ] Add subscription management (list, delete, renew)
- [ ] Handle subscription expiration and renewal logic

#### Phase 3: Email Processing Pipeline
- [ ] Extract email data from webhook payload
- [ ] Store email metadata in Supabase (`emails` table)
- [ ] Implement email content retrieval from Microsoft Graph
- [ ] Add email processing status tracking
- [ ] Create email processing error handling

#### Phase 4: Production Deployment
- [ ] Deploy webhook endpoint to Railway
- [ ] Update Microsoft webhook subscription to production URL
- [ ] Test webhook delivery in production environment
- [ ] Monitor webhook reliability and performance

#### Manual Intervention Required:
- [ ] Install ngrok for local development
- [ ] Configure Microsoft Graph webhook permissions in Azure AD
- [ ] Set up webhook subscription with Microsoft Graph
- [ ] Update webhook endpoint URL in Microsoft Graph (Railway URL)

#### Verification:
- [ ] Webhooks are received correctly (local and production)
- [ ] Webhook validation and security work properly
- [ ] Email data is extracted and stored correctly
- [ ] Webhook subscription management works
- [ ] Error handling and logging function properly
- [ ] Production webhook delivery is reliable

### 5.3 AI Email Analysis Implementation
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 3-4 hours

#### Tasks:
- [ ] Create OpenAI integration in backend
- [ ] Implement email analysis function
- [ ] Create opportunity detection logic
- [ ] Implement confidence scoring
- [ ] Add reasoning extraction
- [ ] Implement comprehensive error handling
- [ ] Add structured logging

#### Manual Intervention Required:
- [ ] Obtain OpenAI API key
- [ ] Configure OpenAI account and billing

#### Verification:
- [ ] AI analysis function works
- [ ] Opportunity detection is accurate
- [ ] Confidence scores are reasonable
- [ ] Reasoning is extracted properly
- [ ] Errors are properly logged and handled

### 5.4 Pipedrive Integration
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [ ] Implement deal existence checking
- [ ] Create deal creation function
- [ ] Add contact management
- [ ] Implement deal update logic
- [ ] Add error handling for API calls
- [ ] Add structured logging for Pipedrive operations

#### Verification:
- [ ] Can check for existing deals
- [ ] New deals are created correctly
- [ ] Contact information is handled
- [ ] API errors are handled gracefully
- [ ] Operations are properly logged

## Phase 6: Error Handling & Logging

### 6.1 Centralized Error Handling
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [ ] Create error handler decorator for FastAPI endpoints
- [ ] Implement structured logging system
- [ ] Create error response utilities
- [ ] Add error tracking and monitoring
- [ ] Implement graceful degradation

#### Verification:
- [ ] Errors are properly caught and logged
- [ ] Error messages are user-friendly
- [ ] System continues to function during errors
- [ ] Error tracking provides useful insights

### 6.2 Logging Infrastructure
**Priority**: Medium | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [ ] Set up structured logging with context
- [ ] Implement log levels and filtering
- [ ] Create log aggregation for debugging
- [ ] Add performance logging
- [ ] Implement log rotation and cleanup

#### Verification:
- [ ] Logs are properly structured and searchable
- [ ] Log levels work correctly
- [ ] Performance metrics are captured
- [ ] Logs can be easily filtered and analyzed

## Phase 7: Testing & Quality Assurance

### 7.1 Unit Testing
**Priority**: Medium | **Manual Intervention**: None | **Estimated Time**: 4-5 hours

#### Tasks:
- [ ] Set up testing framework for both frontend and backend
- [ ] Write tests for authentication
- [ ] Test OAuth flows
- [ ] Test AI analysis functions
- [ ] Test webhook processing
- [ ] Test real-time subscriptions

#### Verification:
- [ ] All tests pass
- [ ] Code coverage is adequate
- [ ] Edge cases are covered
- [ ] Error scenarios are tested

### 7.2 Integration Testing
**Priority**: Medium | **Manual Intervention**: Required | **Estimated Time**: 3-4 hours

#### Tasks:
- [ ] Test end-to-end OAuth flows
- [ ] Test webhook processing pipeline
- [ ] Test AI analysis with real emails
- [ ] Test Pipedrive integration
- [ ] Test error scenarios
- [ ] Test real-time functionality

#### Manual Intervention Required:
- [ ] Send test emails to trigger webhooks
- [ ] Verify deals are created in Pipedrive
- [ ] Check AI analysis results

#### Verification:
- [ ] Complete flow works from email to deal creation
- [ ] Error handling works in production scenarios
- [ ] Performance is acceptable
- [ ] Data integrity is maintained
- [ ] Real-time updates work correctly

## Phase 8: Deployment & Production

### 8.1 Railway Backend Deployment
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 1-2 hours

#### Tasks:
- [x] Configure Railway project
- [x] Set up environment variables
- [x] Configure Python runtime
- [x] Set up custom domains (if needed)
- [x] Configure deployment settings
- [x] Deploy database migrations

#### Manual Intervention Required:
- [x] Create Railway account and project
- [x] Configure environment variables in Railway dashboard
- [x] Set up custom domain (optional)

#### Verification:
- [x] Backend deploys successfully
- [x] All endpoints work in production
- [x] Environment variables are accessible
- [x] Performance is acceptable
- [x] Database migrations are applied

### 8.2 Vercel Frontend Deployment
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 1-2 hours

#### Tasks:
- [x] Configure Vercel project
- [x] Set up environment variables
- [x] Configure Next.js settings
- [x] Set up custom domains (if needed)
- [x] Configure deployment settings

#### Manual Intervention Required:
- [x] Create Vercel account and project
- [x] Configure environment variables in Vercel dashboard
- [x] Set up custom domain (optional)

#### Verification:
- [x] Frontend deploys successfully
- [x] All pages work in production
- [x] Environment variables are accessible
- [x] Performance is acceptable
- [x] API calls to Railway backend work

### 8.3 Production Configuration
**Priority**: Medium | **Manual Intervention**: Required | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Configure production OAuth redirect URIs (Railway URLs)
- [ ] Set up production webhook endpoints (Railway URLs)
- [ ] Configure monitoring and logging
- [ ] Set up error tracking
- [ ] Configure backup strategies
- [x] Test production real-time functionality

#### Manual Intervention Required:
- [x] Update OAuth app configurations with production Railway URLs
- [ ] Configure production webhook subscriptions
- [ ] Set up monitoring tools (optional)

#### Verification:
- [x] OAuth flows work in production
- [ ] Webhooks are received in production
- [ ] Monitoring provides useful insights
- [ ] Error tracking captures issues
- [ ] Real-time updates work in production

## Phase 9: Documentation & Maintenance

### 9.1 Documentation
**Priority**: Low | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [ ] Create user documentation
- [ ] Write API documentation
- [ ] Create deployment guide
- [ ] Document troubleshooting steps
- [ ] Create maintenance procedures
- [ ] Document migration procedures

#### Verification:
- [ ] Documentation is complete and accurate
- [ ] Users can follow setup instructions
- [ ] Troubleshooting guide is helpful
- [ ] Maintenance procedures are clear

### 9.2 Performance Optimization
**Priority**: Low | **Manual Intervention**: None | **Estimated Time**: 2-3 hours

#### Tasks:
- [ ] Optimize database queries
- [ ] Implement caching strategies
- [ ] Optimize AI analysis performance
- [ ] Add performance monitoring
- [ ] Implement rate limiting

#### Verification:
- [ ] Response times are acceptable
- [ ] Database queries are efficient
- [ ] AI analysis completes quickly
- [ ] System handles load gracefully

## Critical Path Analysis

### Must-Have for MVP:
1. **Phase 1**: Project Foundation & Setup (with Railway backend and migrations)
2. **Phase 2**: Authentication & User Management
3. **Phase 3**: OAuth Integration Framework (Pipedrive only initially)
4. **Phase 4**: Real-time Activity Logs & Monitoring
5. **Phase 5**: AI Processing & Webhooks (basic implementation)
6. **Phase 6**: Error Handling & Logging
7. **Phase 8**: Railway Backend Deployment + Vercel Frontend Deployment

### Nice-to-Have for Enhanced Version:
1. **Phase 7**: Comprehensive Testing
2. **Phase 9**: Documentation & Optimization

## Manual Intervention Summary

### Required Manual Steps:
1. **Supabase Setup**: Create account and project
2. **Railway Setup**: Create account and project for backend
3. **Vercel Setup**: Create account and project for frontend
4. **OAuth Provider Registration**: 
   - Pipedrive Developer Hub app creation
   - Microsoft Azure AD app registration
5. **API Key Acquisition**: OpenAI API key
6. **Production Configuration**: Update OAuth redirect URIs and webhook endpoints

### Estimated Manual Time: 4-5 hours
### Estimated Development Time: 30-40 hours
### Total Project Time: 34-45 hours

## Risk Assessment

### High Risk:
- OAuth provider approval processes
- Webhook reliability and delivery
- AI analysis accuracy and cost
- Railway deployment complexity

### Medium Risk:
- Railway Python application scaling
- Supabase RLS policy complexity
- Real-time data synchronization
- Database migration complexity
- Frontend-backend communication

### Low Risk:
- Frontend UI implementation
- Basic authentication flows
- Static content and documentation

## Success Metrics

### Technical Metrics:
- [ ] 99%+ webhook delivery success rate
- [ ] <2 second AI analysis response time
- [ ] <500ms database query response time
- [ ] Zero security vulnerabilities
- [ ] Real-time updates work within 1 second
- [ ] Comprehensive error logging and handling
- [ ] Railway backend uptime >99.9%

### Business Metrics:
- [ ] Users can complete OAuth flows successfully
- [ ] AI correctly identifies 80%+ of sales opportunities
- [ ] Deals are created in Pipedrive within 30 seconds of email
- [ ] System processes 100+ emails per day without issues
- [ ] Dashboard provides real-time visibility into automation activity 