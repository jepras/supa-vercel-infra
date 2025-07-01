from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from lib.oauth_manager import oauth_manager
from lib.supabase_client import supabase_manager
import logging

logger = logging.getLogger(__name__)

async def handler(request):
    """Handle OAuth callback for Pipedrive"""
    try:
        # Parse query parameters
        query_string = request.get('queryStringParameters', {}) or {}
        code = query_string.get('code')
        state = query_string.get('state')
        error = query_string.get('error')
        
        if error:
            logger.error(f"OAuth error from Pipedrive: {error}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': f"""
                <html>
                <body>
                    <h1>OAuth Error</h1>
                    <p>Error: {error}</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
            }
        
        if not code or not state:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': """
                <html>
                <body>
                    <h1>OAuth Error</h1>
                    <p>Missing authorization code or state parameter</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
            }
        
        # Extract user ID from state (format: "user_id:state")
        try:
            user_id, state_token = state.split(':', 1)
        except ValueError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': """
                <html>
                <body>
                    <h1>OAuth Error</h1>
                    <p>Invalid state parameter</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
            }
        
        # Exchange code for tokens
        token_data = await oauth_manager.exchange_code_for_token('pipedrive', code)
        
        # Get user info from Pipedrive
        user_info = await get_pipedrive_user_info(token_data['access_token'])
        
        # Save integration to database
        success = await supabase_manager.save_integration(
            user_id=user_id,
            provider='pipedrive',
            token_data=token_data,
            user_info=user_info
        )
        
        if success:
            # Log successful connection
            await supabase_manager.log_activity(
                user_id=user_id,
                activity_type='oauth_completed',
                status='success',
                message='Pipedrive connected successfully',
                metadata={
                    'provider': 'pipedrive',
                    'user_email': user_info.get('email') if user_info else None
                }
            )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': """
                <html>
                <body>
                    <h1>Success!</h1>
                    <p>Pipedrive has been connected successfully.</p>
                    <p>You can close this window and return to the dashboard.</p>
                    <script>
                        // Send message to parent window
                        if (window.opener) {
                            window.opener.postMessage({ type: 'oauth_success', provider: 'pipedrive' }, '*');
                        }
                        // Close window after a short delay
                        setTimeout(() => window.close(), 2000);
                    </script>
                </body>
                </html>
                """
            }
        else:
            # Log failed connection
            await supabase_manager.log_activity(
                user_id=user_id,
                activity_type='oauth_completed',
                status='error',
                message='Failed to save Pipedrive integration',
                metadata={'provider': 'pipedrive'}
            )
            
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': """
                <html>
                <body>
                    <h1>Error</h1>
                    <p>Failed to save Pipedrive integration. Please try again.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
            }
        
    except Exception as e:
        logger.error(f"Error in Pipedrive OAuth callback: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"""
            <html>
            <body>
                <h1>Error</h1>
                <p>An error occurred while connecting Pipedrive: {str(e)}</p>
                <script>window.close();</script>
            </body>
            </html>
            """
        }

async def get_pipedrive_user_info(access_token: str) -> dict:
    """Get user information from Pipedrive API"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.pipedrive.com/v1/users/me', headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return {
            'id': str(data['data']['id']),
            'email': data['data']['email'],
            'name': data['data']['name']
        }
    except Exception as e:
        logger.error(f"Error getting Pipedrive user info: {str(e)}")
        return {} 