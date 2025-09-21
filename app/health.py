"""
Health Check

This module offers health check endpoints to verify app status for container
orchestration and general liveness and readiness.

Endpoints:
    - /health - Detailed health status for monitoring/debugging
    - /ready - Readiness to serve traffic (external dependencies)
    - /live - Minimal liveness check (process responsiveness only)
"""

import os
import time
from flask import jsonify, current_app
from app.browser.utils import get_mount_base
from app.auth.oidc_client import get_oidc

def register_health_routes(app):
    """
    Register health check routes.
    """

    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Comprehensive health check for monitoring and debugging.

        Provides detailed status of:
        - Mount point accessibility and permissions
        - Basic application configuration
        - Critical application state

        Returns:
            200: Application is healthy and ready
            503: Application has issues (may still be alive but not ready)
        """

        try:
            mount_base = get_mount_base()
            mount_exists = os.path.exists(mount_base)
            mount_readable = (os.access(mount_base, os.R_OK)
                            if mount_exists else False)
            mount_accessible = mount_exists and mount_readable

            # Check if directory can be listed
            try:
                os.listdir(mount_base)
                mount_listable = True
            except (PermissionError, OSError):
                mount_listable = False

            # Check authentication configuration
            mode = current_app.config.get('MODE', 'production')
            auth_configured = True
            if mode != 'development':
                auth_configured = all([
                    current_app.config.get('OAUTH_CLIENT_ID'),
                    current_app.config.get('OAUTH_CLIENT_SECRET'),
                    current_app.config.get('OAUTH_METADATA_URL')
                ])

            health_status = {
                'status': 'healthy',
                'checks': {
                    'mount_exists': mount_exists,
                    'mount_readable': mount_readable,
                    'mount_listable': mount_listable,
                    'auth_configured': auth_configured,
                    'secret_key_set': bool(current_app.config.get('SECRET_KEY'))
                },
                'info': {
                    'mode': mode,
                    'mount_path': mount_base,
                    'version': '1.0.0'
                }
            }

            # Determine overall health - mount must be accessible
            if not mount_accessible or not mount_listable:
                health_status['status'] = 'unhealthy'
                return jsonify(health_status), 503

            return jsonify(health_status), 200

        except (OSError, IOError, KeyError) as error:
            return jsonify({
                'status': 'unhealthy',
                'error': str(error),
                'checks': {},
                'info': {}
            }), 503

    @app.route('/ready', methods=['GET'])
    def readiness_check():
        """
        Readiness check - is app ready to serve traffic?

        Checks external dependencies:
        - Mount point accessibility (required for serving files)
        - OAuth provider connectivity (if configured)
        - Application configuration completeness

        Returns:
            200: Ready to serve traffic
            503: Not ready (don't send traffic, but don't restart)
        """

        try:
            checks = {
                'mount_ready': False,
                'auth_ready': False,
                'config_ready': False
            }

            # Check mount point
            mount_base = get_mount_base()
            checks['mount_ready'] = (
                os.path.exists(mount_base) and
                os.access(mount_base, os.R_OK)
            )

            # Check authentication readiness
            mode = current_app.config.get('MODE', 'production')
            if mode == 'development':
                checks['auth_ready'] = True  # Dev mode always ready
            else:
                # Verify OIDC client can be initialized
                try:
                    oidc_client = get_oidc()
                    checks['auth_ready'] = (
                        oidc_client is not None and
                        hasattr(oidc_client, 'client_id')
                    )

                except (ValueError, KeyError, AttributeError) as error:
                    current_app.logger.warning(
                        "OIDC client initialization failed: %s", error)
                    checks['auth_ready'] = False

            # Check basic configuration
            checks['config_ready'] = all([
                current_app.config.get('SECRET_KEY'),
                current_app.config.get('MODE')
            ])

            # Overall readiness
            ready = all(checks.values())
            status = 'ready' if ready else 'not_ready'
            status_code = 200 if ready else 503

            return jsonify({
                'status': status,
                'checks': checks
            }), status_code

        except (OSError, IOError, KeyError) as error:
            return jsonify({
                'status': 'not_ready',
                'error': str(error),
                'checks': {}
            }), 503

    @app.route('/live', methods=['GET'])
    def liveness_check():
        """
        Liveness check - is the application process alive?

        Minimal check that only verifies the Flask process is responsive.
        Should NOT check external dependencies (mount, OAuth, etc.)

        Only fails if the application process is completely broken.
        Used by orchestrators to determine if container needs restart.

        Returns:
            200: Process is alive and responsive
            500: Process is completely broken (should restart container)
        """

        return jsonify({
            'status': 'alive',
            'timestamp': time.time()
        }), 200
