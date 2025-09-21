"""
Configuration settings for EFS Navigator application.

This module defines the main configuration class that handles environment-specific
settings for development and production deployments. Configuration values are
loaded from environment variables with sensible defaults.

When not running this in a docker container - amazon-efs-utils needs to be installed in order
to interact with EFS properly in a mounted fashion.

Environment Variables:
    MODE: Application mode ('development' or 'production')
    MOUNT_BASE: EFS mount path (default: /mnt/efs)
    LOG_LEVEL: Logging level (default: INFO)
    LOG_FILE: Log file path (default: logs/efs-navigator.log)
    SECRET_KEY: Flask session secret key (REQUIRED in production)
    OAUTH_METADATA_URL: OIDC provider metadata URL
    OAUTH_CLIENT_ID: OAuth client identifier
    OAUTH_CLIENT_SECRET: OAuth client secret
    OAUTH_SCOPE: OAuth scope (default: "openid email profile")
    OAUTH_LOGOUT_URL: OAuth logout endpoint URL
"""

# pylint: disable=too-few-public-methods
import os

class Config:
    """
    Application configuration loaded from environment variables.
    """

    MODE = os.getenv('MODE', 'development')
    MOUNT_BASE = os.path.abspath(os.getenv('MOUNT_BASE', '/mnt/data'))

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'logs/efs-navigator.log')

    SECRET_KEY = os.getenv('SECRET_KEY', 'CHANGE_ME')
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    TOKEN_VALIDATION_INTERVAL_MINUTES = int(os.environ.get('TOKEN_VALIDATION_INTERVAL_MINUTES', 5))
    OAUTH_METADATA_URL = os.environ.get('OAUTH_METADATA_URL')
    OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')
    OAUTH_SCOPE = os.environ.get('OAUTH_SCOPE')
    OAUTH_LOGOUT_URL = os.environ.get('OAUTH_LOGOUT_URL')

def load_config(app):
    """
    Loads config values into the Flask application instance.
    """

    app.config.from_object(Config)
