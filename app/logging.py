
"""
Logging configuration and setup for EFS Navigator application.

This module provides centralized logging configuration with request context
awareness and structured log formatting. It supports both development and
production logging patterns with appropriate handlers and formatters.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request
from flask.logging import default_handler

class RequestFormatter(logging.Formatter):
    """
    Custom log formatter that includes Flask request context information.
    """

    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
            record.user = getattr(getattr(request, 'user', None), 'id', 'anonymous')
        else:
            record.url = None
            record.method = None
            record.remote_addr = None
            record.user = 'system'
        return super().format(record)

def setup_logging(app):
    """
    Configure logging for the Flask application.
    
    Sets up appropriate log handlers, formatters, and levels based on the
    application configuration. In production mode, adds rotating file logs
    for persistence. Always includes a stream handler for immediate output.
        
    Example:
        [2024-01-15 10:30:45] INFO in routes: User accessed file | 
        GET /browse/mount-a/file.txt from 192.168.1.100 user=john.doe
    """

    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = app.config.get('LOG_FILE', 'logs/efs-navigator.log')

    formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s: '
        '%(message)s | %(method)s %(url)s from %(remote_addr)s user=%(user)s'
    )

    # Stream to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)

    # Optional: Rotating file handler for local use
    if app.config['MODE'] == 'production':
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler(log_file,
                                           maxBytes=10 * 1024 * 1024,
                                           backupCount=5)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

    # Flask default handler cleanup
    if default_handler in app.logger.handlers:
        app.logger.removeHandler(default_handler)

    app.logger.setLevel(log_level)
    app.logger.addHandler(stream_handler)

    app.logger.info('EFS Navigator startup complete. Logging configured.')
