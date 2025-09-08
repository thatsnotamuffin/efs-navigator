"""
OAuth/OIDC client configuration for EFS Navigator authentication.

This module sets up OAuth integration using Authlib for production authentication.
It handles OIDC provider configuration and provides access to the OAuth client
for authentication flows. Only OAuth authentication is
supported at this time: July 20, 2025
"""

from authlib.integrations.flask_client import OAuth

# Global variable to store the OIDC client instance
_oidc = None # pylint: disable=invalid-name

# pylint: disable=global-statement
def init_oidc(app):
    """
    Initialize OAuth/OIDC client for the Flask application.
    
    Sets up OAuth client configuration using application settings. Only
    initializes OAuth in production mode - development mode uses automatic
    login for easier testing.
        
    Configuration Required:
        - OAUTH_METADATA_URL: OIDC provider metadata endpoint
        - OAUTH_CLIENT_ID: OAuth client identifier  
        - OAUTH_CLIENT_SECRET: OAuth client secret
        - OAUTH_SCOPE: OAuth scope string (e.g., "openid email profile")
        
    Note:
        The client uses automatic metadata discovery from the provider's
        .well-known/openid-configuration endpoint for configuration.
    """

    global _oidc

    # Only set up OAuth in production mode
    if app.config['MODE'] != 'development':
        oauth = OAuth(app)

        # Register OIDC provider with automatic metadata discovery
        _oidc = oauth.register(
            name='oidc',
            server_metadata_url=app.config['OAUTH_METADATA_URL'],
            client_id=app.config['OAUTH_CLIENT_ID'],
            client_secret=app.config['OAUTH_CLIENT_SECRET'],
            client_kwargs={'scope': app.config['OAUTH_SCOPE']},
        )
    return _oidc

def get_oidc():
    """
    Get the configured OIDC client instance.
    
    Returns:
        OAuth client instance or None if not initialized
        
    Note:
        Returns None in development mode where OAuth is not configured.
    """

    return _oidc
