"""
Error handling and custom error pages for EFS Navigator application.

This module registers comprehensive error handlers for the Flask application,
providing user-friendly error pages and detailed logging for debugging.
It handles both HTTP errors and application-specific template errors.

Error Types Handled:
    - 404 Not Found
    - 500 Internal Server Error
    - Jinja2 Template Errors
    - URL Build Errors
    - General unhandled exceptions
"""

from flask_login import current_user
from flask import render_template, request
from jinja2 import TemplateError
from werkzeug.routing import BuildError

def check_auth_or_return_login():
    """
    Return login prompt if user not authenticated, None if authenticated.
    """

    if not current_user.is_authenticated:
        return '''
        <html><body>
        <h1>Authentication Required</h1>
        <p>You must be logged in to access this application.</p>
        <a href="/login">Login</a>
        </body></html>
        ''', 401
    return None

def register_error_handlers(app):
    """
    Register all error handlers with the Flask application.
    """

    @app.errorhandler(404)
    def page_not_found(_error):
        """
        Handle 404 Not Found errors
        """

        auth_response = check_auth_or_return_login()
        if auth_response:
            return auth_response

        app.logger.warning('404 Not Found: %s', request.path)
        app.logger.warning('Request endpoint was: %s', request.endpoint)

        try:
            result = render_template('404.html'), 404
            return result

        except (TemplateError, OSError, IOError):
            return (f'''<h1>404 - Page Not Found</h1>
                    <p>The page <strong>{request.path}</strong>
                    was not found.</p>''', 404)

    @app.errorhandler(500)
    def server_error(error):
        """
        Handle 500 Internal Server Error.
        """

        auth_response = check_auth_or_return_login()
        if auth_response:
            return auth_response

        app.logger.error('500 Internal Server Error: %s\n%s',
                        request.path, error, exc_info=error)

        try:
            return render_template('500.html'), 500
        except (TemplateError, OSError, IOError) as template_error:
            app.logger.error('Error rendering 500 template: %s',
                           template_error)

            return (f'<h1>500 - Internal Server Error</h1>'
                   f'<p>Error: {error}</p>', 500)

    @app.errorhandler(BuildError)
    def handle_build_error(error):
        """
        Handle URL build errors.
        """

        auth_response = check_auth_or_return_login()
        if auth_response:
            return auth_response

        app.logger.error('URL Build Error: %s', error)

        try:
            return render_template('template_error.html',
                                 error=str(error)), 500

        except (TemplateError, OSError, IOError):
            # Fallback if even the error template fails
            return f'''
            <h1>Template Error</h1>
            <p>There was an error building a URL in the template.</p>
            <p>Error: {error}</p>
            <a href="/">Go back to home</a>
            ''', 500

    @app.errorhandler(TemplateError)
    def handle_template_error(error):
        """
        Handle Jinja2 template rendering errors.
        """

        auth_response = check_auth_or_return_login()
        if auth_response:
            return auth_response

        app.logger.error('Template Error: %s', error)

        try:
            return render_template('template_error.html',
                                 error=str(error)), 500

        except (TemplateError, OSError, IOError):
            return f'''
            <h1>Template Error</h1>
            <p>There was an error rendering the template.</p>
            <p>Error: {error}</p>
            <a href="/">Go back to home</a>
            ''', 500

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """
        Catch-all handler for any unhandled exceptions.
        """

        auth_response = check_auth_or_return_login()
        if auth_response:
            return auth_response

        app.logger.error('Unhandled Exception: %s', error, exc_info=True)

        # Check if it's a template-related error
        if 'template' in str(error).lower() or \
           'jinja' in str(error).lower():
            try:
                return render_template('template_error.html',
                                     error=str(error)), 500

            except (TemplateError, OSError, IOError):
                pass

        # Otherwise use regular 500 handler
        try:
            return render_template('500.html'), 500

        except (TemplateError, OSError, IOError):
            return (f'<h1>500 - Internal Server Error</h1>'
                   f'<p>Something went wrong: {error}</p>', 500)
