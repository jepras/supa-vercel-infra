from http.server import BaseHTTPRequestHandler
import json
import os
import secrets
from datetime import datetime
from urllib.parse import urlencode
from lib.oauth_manager import oauth_manager
from lib.supabase_client import supabase_manager
from middleware import apply_middleware
import logging

logger = logging.getLogger(__name__)

@apply_middleware
async def handler(request):
    """Handle OAuth initiation for Pipedrive"""
    try:
        # Get user ID from request headers (set by middleware)
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized - User ID required'})
            }
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Store state in database for verification
        state_data = {
            'user_id': user_id,
            'provider': 'pipedrive',
            'state': state,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # For now, we'll use a simple approach - in production, you might want to store this in Redis or similar
        # For this example, we'll encode the state with user info
        encoded_state = f"{user_id}:{state}"
        
        # Generate authorization URL
        auth_url = oauth_manager.generate_auth_url('pipedrive', encoded_state)
        
        # Log the OAuth initiation
        await supabase_manager.log_activity(
            user_id=user_id,
            activity_type='oauth_initiated',
            status='success',
            message='Pipedrive OAuth flow initiated',
            metadata={'provider': 'pipedrive'}
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-User-ID'
            },
            'body': json.dumps({
                'auth_url': auth_url,
                'state': encoded_state
            })
        }
        
    except Exception as e:
        logger.error(f"Error initiating Pipedrive OAuth: {str(e)}")
        
        if user_id:
            await supabase_manager.log_activity(
                user_id=user_id,
                activity_type='oauth_initiated',
                status='error',
                message=f'Failed to initiate Pipedrive OAuth: {str(e)}',
                metadata={'provider': 'pipedrive', 'error': str(e)}
            )
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-User-ID'
            },
            'body': json.dumps({'error': 'Failed to initiate OAuth flow'})
        } 