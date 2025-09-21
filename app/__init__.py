"""
Flask application factory for EFS Navigator.

This module implements the application factory pattern for creating
Flask application instances. It handles the complete initialization
sequence including configuration, authentication, routing, and
background services.
"""

# pylint: disable=import-error
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from app.config import load_config
from app.logging import setup_logging
from app.errors import register_error_handlers
from app.auth.login_manager import login_mgr, User
from app.auth.routes import register_auth_routes
from app.routes import register_routes
from app.browser.routes import browser_bp
from app.health import register_health_routes

def create_app():
    """
    Create and configure a Flask application instance.

    This function implements the application factory pattern, creating
    a fully configured Flask application with all necessary components
    initialized. The configuration varies based on the MODE environment
    variable (development vs production).
    """

    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Trust proxy headers
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

    # Load config and session security settings
    load_config(app)
    app.config.update(
        SESSION_COOKIE_SECURE = app.config['MODE'] == 'production',
        SESSION_COOKIE_HTTPONLY = True,
        SESSION_COOKIE_SAMESITE = 'Lax'
    )

    # Setup logging
    setup_logging(app)

    # Initialize Flask-Login
    login_mgr.init_app(app)

    # Register app modules
    register_auth_routes(app)
    register_routes(app)
    register_error_handlers(app)
    register_health_routes(app)
    app.register_blueprint(browser_bp)

    # pylint: disable=import-outside-toplevel
    from app.auth.session import should_validate_token, validate_oauth_session
    from flask_login import current_user, logout_user
    from flask import request, session, redirect, url_for

    @app.before_request
    def check_oauth_session():
        """
        Check OAuth session validity before each request
        """

        # Skip OAuth validation in development mode
        if app.config.get('MODE') == 'development':
            return None

        # Skip for auth endpoints and status files
        skip_endpoints = ['auth.login', 'auth.auth_callback',
                          'auth.logout', 'auth.post_logout']
        if (request.endpoint in skip_endpoints or
            (request.endpoint and request.endpoint.startswith('static'))):
            return None

        # Only check if users is authenticated and that it's time to validate
        if current_user.is_authenticated and should_validate_token():
            if not validate_oauth_session():
                app.logger.info('OAuth session expired for user %s',
                                current_user.id)
                logout_user()
                session.clear()
                return redirect(url_for('auth.login', timeout='oauth_expired'))

        return None

    return app
