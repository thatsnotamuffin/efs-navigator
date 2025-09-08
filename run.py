"""
Application entry point for EFS Navigator.
Supports both local development and containerized deployment.
"""

import os
from app import create_app

def main():
    """
    Main application entry point.
    """

    # Create Flask application
    app = create_app()

    # Get configuration from environment variables
    host = os.getenv('HOST', '127.0.0.1')  # 0.0.0.0 for containers
    port = int(os.getenv('PORT', "5000"))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Log startup information
    app.logger.info("Starting EFS Navigator on %s:%s", host, port)
    app.logger.info("Mode: %s", app.config.get('MODE', 'unknown'))
    app.logger.info("Mount base: %s", app.config.get('MOUNT_BASE', 'not configured'))

    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True  # Better for containers
    )

if __name__ == '__main__':
    main()
