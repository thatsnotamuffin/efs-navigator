"""
Authentication routes for EFS Navigator application.

This module handles user authentication using OAuth/OIDC in production mode
and provides automatic authentication bypass in development mode. It manages
the complete authentication flow including login, OAuth callbacks, and logout.
"""

# pylint: disable=too-many-statements
from datetime import datetime, timedelta
import urllib.parse
from flask import (Blueprint, session, redirect, url_for, request,
                   render_template, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from authlib.common.security import generate_token
from authlib.integrations.base_client import OAuthError
from app.auth.login_manager import User
from app.auth.oidc_client import init_oidc, get_oidc

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

def register_auth_routes(app):
    """
    Register authentication routes with the Flask application.

    Sets up the complete authentication system including OAuth initialization,
    development mode auto-login, and all authentication endpoints. The behavior
    differs significantly between development and production modes.

    Development Mode:
        - Automatic login with test user credentials
        - No OAuth provider required
        - Bypasses authentication for easier development

    Production Mode:
        - Full OAuth/OIDC authentication flow
        - Requires properly configured OAuth provider
        - Secure session handling and logout
    """

    MODE = app.config['MODE'] # pylint: disable=invalid-name

    # Initialize OIDC (noop in dev mode)
    init_oidc(app)

    # Dev mode auto-login for ease of testing
    @app.before_request
    def dev_auto_login():
        """
        Automatically log in users in development mode.

        This function runs before every request in development mode and
        automatically authenticates users with test credentials. This allows
        developers to test the application without setting up OAuth.

        Note:
            Only active in development mode. Has no effect in production.
        """

        # Only run in development mode
        if MODE != 'development':
            return None

        # Skip auto-login for certain endpoints
        if request.endpoint and request.endpoint.startswith('static'):
            return None

        skip_endpoints = ['auth.login', 'auth.auth_callback',
                          'auth.logout', 'auth.post_logout']
        if request.endopint in skip_endpoints:
            return None

        if request.endpoint and request.endpoint.startswith('debug'):
            return None

        if request.endpoint is None:
            return None

        # Auto-login if user is not already authenticated
        if not current_user.is_authenticated:
            dev_user_info = {
                'sub': 'dev-user',
                'name': 'Dev User',
                'email': 'dev@example.com'
            }
            session['user'] = dev_user_info
            login_user(User(**dev_user_info))

        return None

    # Login route
    @auth_bp.route('/login', strict_slashes=False)
    def login():
        """
        Handle user login requests.

        In development mode, automatically logs in with test credentials.
        In production mode, initiates OAuth authentication flow with the
        configured OIDC provider.
        """

        # Development mode: immediate auto-login
        if MODE == 'development':
            if not current_user.is_authenticated:
                dev_user_info = {
                    'sub': 'dev-user',
                    'name': 'Dev User',
                    'email': 'dev@example.com'
                }
                session['user'] = dev_user_info
                login_user(User(**dev_user_info))
            return redirect(request.args.get('next') or url_for('dashboard'))

        # Production mode: OAuth flow
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        # Verify OAuth is configured
        if not get_oidc():
            return 'OAuth not configured for production mode', 500

        # Store the intended destination
        session['next'] = request.args.get('next')

        # Generate nonce for CSRF protection
        nonce = generate_token()
        session['_nonce'] = nonce

        # Redirect to OAuth provider
        redirect_uri = url_for('auth.auth_callback', _external=True)
        return get_oidc().authorize_redirect(redirect_uri=redirect_uri, nonce=nonce)

    # OIDC callback handler
    @auth_bp.route('/auth/callback', strict_slashes=False)
    def auth_callback():
        """
        Handle OAuth authentication callback from provider.

        This endpoint receives the authorization code from the OAuth provider
        and exchanges it for user information. It validates the response and
        creates a user session upon successful authentication.
        """

        # Development mode bypass
        if MODE == 'development':
            return redirect(url_for('dashboard'))

        # Verify OAuth is configured
        if not get_oidc():
            return 'OAuth not configured', 500

        try:
            # Retrieve nonce for validation
            nonce = session.get('_nonce')

            # Exchange authorization code for token
            token = get_oidc().authorize_access_token()

            if token.get('access_token'):
                session['access_token'] = token['access_token']

                # Calculate and store expiration time
                expires_in = token.get('expires_in', 3600)
                expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                session['token_expires_at'] = expires_at.isoformat()

             # Store for logout
            if token.get('id_token'):
                session['id_token'] = token['id_token']

            # Get user information from token or userinfo endpoint
            userinfo = (
                token.get('userinfo')
                or get_oidc().parse_id_token(token, nonce=nonce) if token.get('id_token') and nonce
                else get_oidc().userinfo(token=token)
            )

            if not userinfo:
                raise ValueError('Failed to retrieve user info')

            # Clean up session security data - # Store user information
            session.pop('_nonce', None)
            session['user'] = userinfo

            # Create user object and log in
            user = User(
                userinfo['sub'],
                userinfo.get('name') or userinfo.get('preferred_username'),
                userinfo.get('email')
            )
            login_user(user)

            # Log successful authentication
            current_app.logger.info(f'User {user.id} authenticated successfully')

            return redirect(session.pop('next', None) or url_for('dashboard'))

        except (OAuthError, ValueError, KeyError) as error:
            session.clear()
            return f'Error during authentication: {error}', 500

    # Build logout URL for OAuth handling
    def build_logout_url(logout_url, post_logout_redirect, client_id, id_token=None):
        """
        Build logout URL with fallback for older OAuth implementations.

        Tries modern OIDC approach first (post_logout_redirect_uri + client_id),
        then falls back to legacy approach (redirect_uri) for older OAuth providers.
        """

        # Try modern OIDC approach first
        try:
            params = {
                'post_logout_redirect_uri': post_logout_redirect,
                'client_id': client_id
            }

            if id_token:
                params['id_token_hint'] = id_token

            query_string = urllib.parse.urlencode(params)
            return f"{logout_url}?{query_string}"

        except (ValueError, TypeError) as error:
            # Fallback to legacy approach
            current_app.logger.warning("Using legacy logout approach: %s",
                                      error)
            legacy_params = {'redirect_uri': post_logout_redirect}
            query_string = urllib.parse.urlencode(legacy_params)
            return f"{logout_url}?{query_string}"

    # Logout handler
    @auth_bp.route('/logout', strict_slashes=False)
    @login_required
    def logout():
        """
        Handle user logout requests with backwards compatibility.

        Supports both modern OIDC logout flows and legacy OAuth implementations.
        """

        # Log the logout attempt
        current_app.logger.info(f'User {current_user.id} logging out')

        # Store id_token before clearing session (if needed for logout)
        id_token = session.get('id_token')

        # Clear Flask-Login session
        logout_user()
        session.clear()

        # Development mode: simple redirect
        if MODE == 'development':
            return redirect(url_for('auth.post_logout'))

        # Production mode: OAuth provider logout if configured
        logout_url = current_app.config.get('OAUTH_LOGOUT_URL')
        if logout_url:
            post_logout_redirect = url_for('auth.post_logout', _external=True)
            client_id = current_app.config.get('OAUTH_CLIENT_ID')

            # Use backwards compatible logout URL builder
            full_logout_url = build_logout_url(
                logout_url=logout_url,
                post_logout_redirect=post_logout_redirect,
                client_id=client_id,
                id_token=id_token
            )

            current_app.logger.info(f"Redirecting to logout URL: {full_logout_url}")
            return redirect(full_logout_url)

        # Fallback to local logout if no OAuth logout URL
        return redirect(url_for('auth.post_logout'))

    # Logged-out confirmation page
    @auth_bp.route('/post-logout', strict_slashes=False)
    def post_logout():
        """
        Display logout confirmation page.

        This page is shown after successful logout to confirm the user has
        been signed out. It provides a clean landing page with options to
        log back in if needed.
        """

        # Clear session as safety measure
        session.clear()
        try:
            return render_template('logout.html')

        except (OSError, IOError) as error:
            # Fallback HTML if template fails
            current_app.logger.warning("Template error in post_logout: %s",
                                      error)
            return '''
            <html><body>
            <h1>Logged Out</h1>
            <p>You have been logged out of EFS Navigator.</p>
            <a href='/login'>Login Again</a>
            </body></html>
            '''

    # Register the Blueprint
    app.register_blueprint(auth_bp)
