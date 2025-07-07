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

### 3.2 OAuth Provider Setup - COMPLETED ✅
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

### 4.2 Integration Management UI - COMPLETED ✅
**Priority**: Medium | **Manual Intervention**: None | **Estimated Time**: 3-4 hours

#### Tasks:
- [x] Create integration cards for Pipedrive and Outlook
- [x] Implement connection/disconnection flows
- [x] Create integration status indicators
- [x] Add automation toggle switches
- [x] Implement integration settings (webhook management)

#### Verification:
- [x] Integration cards display correct status
- [x] Connect/disconnect buttons work
- [x] Status updates in real-time
- [x] Settings can be modified (webhook subscriptions)

### 4.3 Real-time Activity Logs & Monitoring - COMPLETED ✅
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 3-4 hours

#### Tasks:
- [x] Create real-time subscription hooks
- [x] Implement activity logs table with live updates
- [x] Create log filtering and search
- [x] Add real-time opportunity detection logs
- [x] Implement log export functionality
- [x] Add loading states for real-time data

#### Verification:
- [x] Logs display correctly
- [x] Real-time updates work without page refresh
- [x] Filtering and search work
- [x] Live updates function properly
- [x] Export functionality works

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

### 5.2 Webhook Implementation (Outlook First) - COMPLETED ✅
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 3-4 hours

#### Phase 1: Local Development Setup - COMPLETED ✅
- [x] Install and configure ngrok for local webhook testing
- [x] Create webhook endpoint in existing Railway backend (`/api/webhooks/microsoft/email`)
- [x] Implement webhook validation and security (Microsoft Graph validation)
- [x] Add basic webhook logging and error handling
- [x] Test webhook reception locally with ngrok

#### Phase 2: Microsoft Graph Webhook Subscription - COMPLETED ✅
- [x] Create webhook subscription endpoint (`/api/webhooks/microsoft/subscribe`)
- [x] Implement subscription creation with Microsoft Graph API
- [x] Add subscription management (list, delete, renew)
- [x] Handle subscription expiration and renewal logic

#### Phase 3: Email Processing Pipeline - COMPLETED ✅
- [x] Extract email data from webhook payload
- [x] Store email metadata in Supabase (`emails` table)
- [x] Implement email content retrieval from Microsoft Graph
- [x] Add email processing status tracking
- [x] Create email processing error handling

#### Phase 4: Production Deployment - COMPLETED ✅
- [x] Deploy webhook endpoint to Railway
- [x] Update Microsoft webhook subscription to production URL
- [x] Test webhook delivery in production environment
- [x] Monitor webhook reliability and performance
- [x] Fix CORS configuration for production domains
- [x] Update frontend to use Railway production URLs

#### Manual Intervention Required:
- [x] Install ngrok for local development
- [x] Configure Microsoft Graph webhook permissions in Azure AD
- [x] Set up webhook subscription with Microsoft Graph (production)
- [x] Update webhook endpoint URL in Microsoft Graph (Railway URL)

#### Verification:
- [x] Webhooks are received correctly (local)
- [x] Webhook validation and security work properly
- [x] Email data is extracted and stored correctly
- [x] Webhook subscription management works
- [x] Error handling and logging function properly
- [x] Production webhook delivery is reliable
- [x] Emails are successfully stored in database from production webhooks
- [x] Frontend can create and manage webhook subscriptions

### 5.3 AI Email Analysis Implementation - ENHANCED PLAN
**Priority**: High | **Manual Intervention**: Required | **Estimated Time**: 10-12 hours (2 weeks)

#### Phase 1: Simple Integrations (Week 1) - Notebook Prototyping & Basic Integration
**Goal**: Get basic AI analysis working with simple prompts

##### Tasks:
- [ ] Create Jupyter notebook for AI analysis prototyping (`notebooks/ai_analysis_prototype.ipynb`)
- [ ] Set up OpenRouter API integration with OpenAI-compatible client
- [ ] Test multiple models (GPT-4, Claude, Gemini) for accuracy comparison
- [ ] Create simple prompt-based email analysis with OpenRouter
- [ ] Test with 10+ sample emails for accuracy validation
- [ ] Implement basic Pipedrive API integration (deal creation/search)
- [ ] Create end-to-end flow in notebook environment
- [ ] Add basic error handling and logging
- [ ] Create cost optimization notebook (`notebooks/cost_optimization.ipynb`)

##### Files to Create:
- [ ] `notebooks/ai_analysis_prototype.ipynb`
- [ ] `notebooks/model_comparison.ipynb` (OpenRouter model testing)
- [ ] `notebooks/cost_optimization.ipynb` (cost analysis)
- [ ] `backend/app/agents/email_analyzer.py` (simple version with OpenRouter)
- [ ] `backend/app/agents/pipedrive_manager.py` (basic version)
- [ ] `backend/app/lib/ai_client.py` (OpenRouter implementation)
- [ ] `backend/app/config/ai_models.py` (model configurations)

##### Phase 1 Validation Milestones:
- [ ] **Day 2**: AI can classify 10 sample emails with >80% accuracy using OpenRouter
- [ ] **Day 3**: Pipedrive API can create/search deals successfully
- [ ] **Day 4**: Model comparison shows best performing model for our use case
- [ ] **Day 5**: End-to-end flow works in notebook environment
- [ ] **Day 6**: Cost optimization analysis completed
- [ ] **Day 7**: Ready for webhook integration with selected model

#### Phase 2: Production Integration (Week 2) - Webhook Pipeline & Advanced Features
**Goal**: Integrate AI analysis into webhook pipeline with monitoring

##### Tasks:
- [ ] Connect AI analysis to existing webhook pipeline with OpenRouter
- [ ] Implement function calling for structured AI output
- [ ] Add comprehensive error handling and retry logic
- [ ] Create frontend email display component
- [ ] Implement real-time AI analysis results in dashboard
- [ ] Add monitoring and performance tracking
- [ ] Implement rate limiting and cost controls for OpenRouter
- [ ] Add model switching capabilities in production
- [ ] Create cost monitoring dashboard

##### Files to Create:
- [ ] `backend/app/agents/__init__.py`
- [ ] `backend/app/agents/analyze_email.py` (production version with OpenRouter)
- [ ] `backend/app/agents/check_deal_exists.py`
- [ ] `backend/app/agents/create_deal.py`
- [ ] `backend/app/agents/orchestrator.py` (agent coordination)
- [ ] `backend/app/agents/prompts.py` (prompt templates)
- [ ] `src/components/email-viewer.tsx`
- [ ] `src/components/ai-analysis.tsx`
- [ ] `src/components/deal-status.tsx`
- [ ] `src/components/cost-monitor.tsx` (OpenRouter cost monitoring)

##### Phase 2 Additional Files (Monitoring):
- [ ] `backend/app/monitoring/agent_logger.py` (structured logging)
- [ ] `backend/app/monitoring/metrics.py` (performance tracking)
- [ ] `backend/app/monitoring/cost_tracker.py` (OpenRouter cost monitoring)
- [ ] `backend/app/config/rate_limits.py` (API rate limiting)
- [ ] `backend/app/config/ai_models.py` (model management)

#### Manual Intervention Required:
- [ ] Obtain OpenRouter API key
- [ ] Configure OpenRouter account and billing
- [ ] Set up monitoring dashboard (optional)
- [ ] Configure model preferences and cost limits

#### Verification:
- [ ] AI analysis function works with >80% accuracy using OpenRouter
- [ ] Opportunity detection provides reasonable confidence scores
- [ ] Reasoning is extracted and displayed properly
- [ ] Errors are properly logged and handled with retry logic
- [ ] End-to-end flow: Email → AI Analysis → Pipedrive Deal creation
- [ ] Real-time updates work in dashboard
- [ ] Performance metrics are tracked and displayed
- [ ] Rate limiting prevents API abuse
- [ ] Cost monitoring shows OpenRouter usage and costs
- [ ] Model switching works correctly in production
- [ ] Cost controls prevent excessive spending
- [ ] GDPR compliance: No email storage for non-opportunities
- [ ] Only opportunity data stored in database
- [ ] Existing deals detected but never updated

### 5.4 Pipedrive Integration - ENHANCED PLAN
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 4-6 hours (integrated with AI implementation)

#### Phase 1: Basic Integration (Week 1) - Part of AI Prototyping
**Goal**: Get basic Pipedrive API operations working

##### Tasks:
- [ ] Implement deal existence checking with Pipedrive API
- [ ] Create basic deal creation function (only for new deals)
- [ ] Add contact management (create/update contacts)
- [ ] Test API operations in notebook environment
- [ ] Add basic error handling for API calls
- [ ] Implement structured logging for Pipedrive operations
- [ ] Ensure no deal updates - only creation of new deals

##### Files to Create:
- [ ] `backend/app/agents/pipedrive_manager.py` (basic version)
- [ ] `backend/app/lib/pipedrive_client.py` (API wrapper)
- [ ] `notebooks/pipedrive_integration_test.ipynb`

#### Phase 2: Production Integration (Week 2) - Advanced Features
**Goal**: Full Pipedrive integration with AI orchestration

##### Tasks:
- [ ] Implement advanced deal management (stages, values, custom fields for new deals only)
- [ ] Add contact deduplication and merging logic
- [ ] Create deal existence checking logic (no updates for existing deals)
- [ ] Implement comprehensive error handling and retry logic
- [ ] Add Pipedrive webhook handling for deal updates (read-only monitoring)
- [ ] Create frontend deal status display component
- [ ] Ensure existing deals are logged but never modified

##### Files to Create:
- [ ] `backend/app/agents/check_deal_exists.py` (production version)
- [ ] `backend/app/agents/create_deal.py` (production version)
- [ ] `backend/app/agents/contact_manager.py`
- [ ] `backend/app/webhooks/pipedrive.py`
- [ ] `src/components/deal-status.tsx`
- [ ] `src/components/contact-manager.tsx`

#### Verification:
- [ ] Can check for existing deals with high accuracy
- [ ] New deals are created correctly with proper metadata
- [ ] Contact information is handled and deduplicated
- [ ] API errors are handled gracefully with retry logic
- [ ] Operations are properly logged with structured data
- [ ] Existing deals are detected and logged (no updates made)
- [ ] Frontend displays deal status in real-time
- [ ] No duplicate deals are created
- [ ] GDPR compliance maintained with minimal data storage

## Phase 6: Error Handling & Logging - ENHANCED PLAN

### 6.1 Centralized Error Handling
**Priority**: High | **Manual Intervention**: None | **Estimated Time**: 3-4 hours

#### Tasks:
- [ ] Create error handler decorator for FastAPI endpoints
- [ ] Implement structured logging system with context
- [ ] Create error response utilities with proper HTTP status codes
- [ ] Add error tracking and monitoring with correlation IDs
- [ ] Implement graceful degradation for AI and API failures
- [ ] Add retry logic for transient failures
- [ ] Create error categorization (user errors vs system errors)

#### Files to Create:
- [ ] `backend/app/lib/error_handler.py` (decorator and utilities)
- [ ] `backend/app/lib/retry_logic.py` (retry mechanisms)
- [ ] `backend/app/monitoring/error_tracker.py` (error tracking)

#### Verification:
- [ ] Errors are properly caught and logged with context
- [ ] Error messages are user-friendly and actionable
- [ ] System continues to function during errors with graceful degradation
- [ ] Error tracking provides useful insights with correlation IDs
- [ ] Retry logic handles transient failures appropriately
- [ ] Error categorization helps with debugging and user support

### 6.2 Logging Infrastructure - ENHANCED
**Priority**: Medium | **Manual Intervention**: None | **Estimated Time**: 3-4 hours

#### Tasks:
- [ ] Set up structured logging with context and correlation IDs
- [ ] Implement log levels and filtering with proper configuration
- [ ] Create log aggregation for debugging with search capabilities
- [ ] Add performance logging with timing and resource usage
- [ ] Implement log rotation and cleanup with retention policies
- [ ] Add AI-specific logging for prompt/response tracking
- [ ] Create monitoring dashboards for log analysis

#### Files to Create:
- [ ] `backend/app/monitoring/agent_logger.py` (AI-specific logging)
- [ ] `backend/app/monitoring/metrics.py` (performance tracking)
- [ ] `backend/app/config/logging_config.py` (logging configuration)
- [ ] `backend/app/lib/logger.py` (structured logging utilities)

#### Verification:
- [ ] Logs are properly structured and searchable with correlation IDs
- [ ] Log levels work correctly with proper filtering
- [ ] Performance metrics are captured and displayed
- [ ] Logs can be easily filtered and analyzed in production
- [ ] AI operations are logged with prompts and responses
- [ ] Log retention policies are properly configured



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

### 8.3 Production Configuration - COMPLETED ✅
**Priority**: Medium | **Manual Intervention**: Required | **Estimated Time**: 2-3 hours

#### Tasks:
- [x] Configure production OAuth redirect URIs (Railway URLs)
- [x] Set up production webhook endpoints (Railway URLs)
- [x] Configure monitoring and logging
- [x] Set up error tracking
- [x] Configure backup strategies
- [x] Test production real-time functionality

#### Manual Intervention Required:
- [x] Update OAuth app configurations with production Railway URLs
- [x] Configure production webhook subscriptions
- [x] Set up monitoring tools (optional)

#### Verification:
- [x] OAuth flows work in production
- [x] Webhooks are received in production
- [x] Monitoring provides useful insights
- [x] Error tracking captures issues
- [x] Real-time updates work in production

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


## Critical Path Analysis

### Must-Have for MVP:
1. **Phase 1**: Project Foundation & Setup (with Railway backend and migrations) ✅
2. **Phase 2**: Authentication & User Management ✅
3. **Phase 3**: OAuth Integration Framework (Pipedrive and Microsoft) ✅
4. **Phase 4**: Real-time Activity Logs & Monitoring ✅
5. **Phase 5**: Webhooks & Email Processing ✅
6. **Phase 6**: Error Handling & Logging ✅
7. **Phase 8**: Railway Backend Deployment + Vercel Frontend Deployment ✅

### Next Priority for Enhanced Version:
1. **Phase 5.3**: AI Email Analysis Implementation
2. **Phase 5.4**: Pipedrive Integration (Deal Creation)
3. **Phase 7**: Comprehensive Testing
4. **Phase 9**: Documentation & Optimization

### Nice-to-Have for Enhanced Version:
1. **Phase 7**: Comprehensive Testing
2. **Phase 9**: Documentation & Optimization

## Implementation Strategy & Technology Decisions

### AI/LLM Technology Stack
**Decision**: OpenRouter API (not LangChain, not direct OpenAI)


### Agent Architecture
**Decision**: Multiple specialized agents with orchestration

#### Agent Structure:
1. **Email Analysis Agent**: AI-powered opportunity detection
2. **Deal Management Agent**: Pipedrive API operations
3. **Orchestrator Agent**: Coordinates agent interactions

#### Implementation Pattern:
```python
# backend/app/agents/orchestrator.py
class AgentOrchestrator:
    async def process_email(self, email_data: dict) -> dict:
        # 1. Analyze email with AI
        analysis = await self.email_analyzer.analyze(email_data)
        
        # 2. If opportunity detected, check for existing deal
        if analysis.is_opportunity:
            existing_deal = await self.deal_manager.check_exists(email_data.recipient)
            
            # 3. Create deal only if none exists (no updates)
            if not existing_deal:
                deal = await self.deal_manager.create_deal(analysis, email_data)
            else:
                # Log existing deal detection (no modification)
                await self.logger.log_existing_deal(existing_deal, analysis)
                
        # 4. Log all activities (GDPR compliant - no email storage for non-opportunities)
        await self.logger.log_activity(analysis, deal if 'deal' in locals() else None)
```

### Development Workflow
**Decision**: Notebook-first prototyping, then production integration

#### Phase 1 Workflow:
1. **Day 1-2**: Jupyter notebook prototyping
2. **Day 3-4**: Basic backend integration
3. **Day 5-6**: Webhook pipeline connection
4. **Day 7**: End-to-end testing

#### Phase 2 Workflow:
1. **Week 2**: Production features and monitoring
2. **Week 3**: Advanced features and optimization

### File Structure for Implementation
```
backend/app/agents/
├── __init__.py
├── email_analyzer.py      # AI email analysis via OpenRouter
├── deal_manager.py        # Pipedrive deal operations
├── orchestrator.py        # Agent coordination
└── prompts.py            # AI prompt templates

notebooks/
├── ai_analysis_prototype.ipynb
├── prompt_optimization.ipynb
├── model_comparison.ipynb    # Test different OpenRouter models
└── cost_optimization.ipynb   # Compare model costs and performance

backend/app/monitoring/
├── agent_logger.py        # AI-specific logging
├── metrics.py            # Performance tracking
├── cost_tracker.py       # OpenRouter cost monitoring
└── error_tracker.py      # Error tracking

backend/app/config/
├── rate_limits.py        # API rate limiting
├── logging_config.py     # Logging configuration
└── ai_models.py          # OpenRouter model configurations
```

## Current Status Summary

### ✅ Completed Phases:
- **Phase 1**: Project Foundation & Setup
- **Phase 2**: Authentication & User Management  
- **Phase 3**: OAuth Integration Framework
- **Phase 4**: Frontend Dashboard & UI
- **Phase 5.1**: Database Schema for Email Processing
- **Phase 5.2**: Webhook Implementation (Microsoft Graph)
- **Phase 8**: Deployment & Production

### 🚧 In Progress:
- **Phase 5.3**: AI Email Analysis Implementation (Enhanced Plan)
- **Phase 5.4**: Pipedrive Integration (Enhanced Plan)

### 📋 Next Steps:
1. **Week 1**: Notebook prototyping and basic AI integration
2. **Week 2**: Production webhook integration and monitoring
3. **Week 3**: Advanced features and comprehensive testing
4. **Week 4**: Documentation and optimization

## Manual Intervention Summary


## Success Criteria
1. Users can authenticate via Supabase (single-user accounts)
2. Users can connect Pipedrive and Outlook via OAuth  
3. System detects when user sends emails via Outlook webhook
4. AI analyzes sent emails and identifies sales opportunities
5. System checks Pipedrive for existing deals with email recipients
6. New deals are automatically created in Pipedrive when opportunities are detected (no updates to existing deals)
7. All activity is logged with GDPR-compliant data (no email content stored for non-opportunities)
8. Users can view opportunity detection and deal creation activity in dashboard
9. Dashboard updates in real-time via Supabase subscriptions
10. Comprehensive error handling and logging throughout the system
11. GDPR compliance maintained with minimal data storage
12. No duplicate deals created in Pipedrive

#### AI Email Analysis with Error Handling
```python
# backend/app/agents/analyze_email.py
import openai
from ..lib.supabase_client import supabase
from ..lib.error_handler import handle_errors
from ..lib.logger import get_logger
import hashlib
import json
import os

logger = get_logger(__name__)

@handle_errors
async def analyze_email(user_id: str, email_content: str, recipient_email: str):
    """Analyze sent email for sales opportunities using AI via OpenRouter"""
    
    logger.info("Starting email analysis", extra={
        "user_id": user_id,
        "recipient_email": recipient_email,
        "content_length": len(email_content),
        "ai_model": os.getenv("AI_MODEL", "openai/gpt-4-1106-preview")
    })
    
    # Create hash for deduplication (GDPR-compliant)
    email_hash = hashlib.sha256(email_content.encode()).hexdigest()
    
    # Check if we've already processed this email
    existing = supabase.table('opportunity_logs').select('*').eq('email_hash', email_hash).execute()
    if existing.data:
        logger.info("Email already processed", extra={"email_hash": email_hash})
        return {"already_processed": True}
    
    # Initialize OpenRouter client
    client = openai.OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    
    # AI analysis with OpenRouter
    ai_prompt = f"""
    Analyze this email to determine if it represents a sales opportunity:
    
    Email content: {email_content}
    Recipient: {recipient_email}
    
    Respond with JSON:
    {{
        "is_opportunity": true/false,
        "confidence": 0.0-1.0,
        "reasoning": "explanation",
        "deal_title": "suggested deal name",
        "deal_value": estimated_value_or_null,
        "deal_stage": "prospecting/proposal/negotiation"
    }}
    """
    
    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL", "openai/gpt-4-1106-preview"),
        messages=[{"role": "user", "content": ai_prompt}],
        response_format={"type": "json_object"}
    )
    
    ai_result = json.loads(response.choices[0].message.content)
    
    # Log activity for real-time updates (always log the analysis)
    activity_data = {
        "user_id": user_id,
        "activity_type": "email_analyzed",
        "status": "success",
        "message": f"Email analyzed for {recipient_email}",
        "metadata": {
            "opportunity_detected": ai_result["is_opportunity"],
            "confidence": ai_result["confidence"],
            "ai_model": os.getenv("AI_MODEL", "openai/gpt-4-1106-preview")
        }
    }
    supabase.table('activity_logs').insert(activity_data).execute()
    
    # Only store opportunity data if opportunity is detected (GDPR compliance)
    if ai_result["is_opportunity"]:
        log_data = {
            "user_id": user_id,
            "email_hash": email_hash,
            "recipient_email": recipient_email,
            "opportunity_detected": ai_result["is_opportunity"],
            "ai_confidence_score": ai_result["confidence"],
            "ai_reasoning": ai_result["reasoning"]
        }
        supabase.table('opportunity_logs').insert(log_data).execute()
        
        logger.info("Email analysis completed - opportunity detected", extra={
            "opportunity_detected": ai_result["is_opportunity"],
            "confidence": ai_result["confidence"],
            "ai_model": os.getenv("AI_MODEL", "openai/gpt-4-1106-preview")
        })
        
        return {
            "opportunity_detected": True,
            "ai_analysis": ai_result,
            "next_step": "check_deal_exists"
        }
    else:
        # No opportunity detected - only log activity, don't store email data
        logger.info("Email analysis completed - no opportunity detected", extra={
            "opportunity_detected": ai_result["is_opportunity"],
            "confidence": ai_result["confidence"],
            "ai_model": os.getenv("AI_MODEL", "openai/gpt-4-1106-preview")
        })
        
        return {"opportunity_detected": False}
``` 