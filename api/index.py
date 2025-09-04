from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from io import BytesIO

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from subtitle_generator import app as application

def vercel_handler(event, context):
    # Create a test request from the event
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('rawQuery', ''),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'HTTP_HOST': event['headers'].get('host', 'localhost'),
        'wsgi.url_scheme': 'https' if event['headers'].get('x-forwarded-proto') == 'https' else 'http',
        'wsgi.input': BytesIO(event.get('body', '').encode('utf-8') if event.get('body') else b''),
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.run_once': False,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
    }
    
    # Add headers to environ
    for key, value in event.get('headers', {}).items():
        key = 'HTTP_' + key.upper().replace('-', '_')
        if key not in ('HTTP_CONTENT_LENGTH', 'HTTP_CONTENT_TYPE'):
            environ[key] = value
    
    # Handle content length and type
    if 'content-length' in event['headers']:
        environ['CONTENT_LENGTH'] = event['headers']['content-length']
    if 'content-type' in event['headers']:
        environ['CONTENT_TYPE'] = event['headers']['content-type']
    
    # Create a response object
    response = {}
    response_body = []
    
    def start_response(status, response_headers, exc_info=None):
        nonlocal response
        response['statusCode'] = int(status.split(' ')[0])
        response['headers'] = dict(response_headers)
        response['multiValueHeaders'] = {}
        response['isBase64Encoded'] = False
        return lambda data: response_body.append(data)
    
    # Process the request
    result = application(environ, start_response)
    
    # Collect response body
    for data in result:
        response_body.append(data)
    
    if response_body:
        response['body'] = b''.join(response_body).decode('utf-8')
    
    # Return the response
    return response

# This is the entry point for Vercel
def handler(event, context):
    return vercel_handler(event, context)