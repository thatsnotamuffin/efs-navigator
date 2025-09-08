"""
Gunicorn WSGI server config

Configures the Gunicorn web server for production deployment
"""

import os

# Server
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')
backlog = int(os.getenv('GUNICORN_BACKLOG', '2048'))

# Workers
workers = int(os.getenv('GUNICORN_WORKERS', '2'))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '2'))

# Worker Restart
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '100'))

# Load Application
preload_app = os.getenv('GUNICORN_PRELOAD_APP', 'True').lower() == 'true'

# Logging
accesslog = os.getenv('GUNICORN_ACCESSLOG', '-')
errorlog = os.getenv('GUNICORN_ERRORLOG', '-')
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')

# Process Name
proc_name = os.getenv('GUNICORN_PROC_NAME', 'navigator')
