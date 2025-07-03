import os
import jwt
import json
from typing import Dict, Any, Optional
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client for token verification
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_service_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")

supabase: Client = create_client(supabase_url, supabase_service_key)

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return user data"""
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Verify token with Supabase
        result = supabase.auth.get_user(token)
        
        if result.user:
            return {
                'id': result.user.id,
                'email': result.user.email,
                'aud': result.user.aud,
                'role': result.user.role
            }
        
        return None
    except Exception as e:
        logger.error(f"Error verifying JWT token: {str(e)}")
        return None

def auth_middleware(request: Dict[str, Any]) -> Dict[str, Any]:
    """Middleware to authenticate API requests"""
    try:
        # Get authorization header
        headers = request.get('headers', {})
        auth_header = headers.get('authorization') or headers.get('Authorization')
        
        if not auth_header:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Authorization header required'})
            }
        
        # Verify token
        user_data = verify_jwt_token(auth_header)
        
        if not user_data:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid or expired token'})
            }
        
        # Add user ID to request headers for downstream handlers
        if 'headers' not in request:
            request['headers'] = {}
        
        request['headers']['X-User-ID'] = user_data['id']
        request['headers']['X-User-Email'] = user_data['email']
        
        return request
        
    except Exception as e:
        logger.error(f"Error in auth middleware: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Authentication error'})
        }

def apply_middleware(handler_func):
    """Decorator to apply authentication middleware to handler functions"""
    def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
        # Apply auth middleware
        auth_result = auth_middleware(request)
        
        # If middleware returned an error response, return it
        if 'statusCode' in auth_result:
            return auth_result
        
        # Otherwise, call the original handler with the modified request
        return handler_func(auth_result)
    
    return wrapper 