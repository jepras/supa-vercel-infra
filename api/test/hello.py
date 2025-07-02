from http.server import BaseHTTPRequestHandler
import json

async def handler(request):
    """Simple test endpoint to verify Python functions work"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps({
            'message': 'Hello from Python serverless function!',
            'timestamp': '2025-07-02T06:05:00Z',
            'status': 'working'
        })
    } 