from http.server import BaseHTTPRequestHandler
import json

def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            'message': 'Python API is working!',
            'python_version': '3.x',
            'timestamp': '2025-07-01T12:00:00Z'
        })
    } 