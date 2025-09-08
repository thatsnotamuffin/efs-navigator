"""
Flask-Login integration and user management for EFS Navigator.

This module sets up Flask-Login for session management and defines the User
model for authenticated users. It handles both development mode (with automatic
login) and production mode (with OAuth authentication). Only OAuth authentication is
supported at this time: July 20, 2025
"""

from flask_login import LoginManager, UserMixin
from flask import session

# Initialize Flask-Login manager
login_mgr = LoginManager()
login_mgr.login_view = 'auth.login' # Redirect unauthenticated users here
login_mgr.login_message = 'Please log in to access this page.'


class User(UserMixin):
    """
    User model for authenticated users in EFS Navigator.
    
    This class represents an authenticated user with profile information
    from the OAuth provider. It implements Flask-Login's UserMixin interface
    to provide standard authentication methods.
    
    Attributes:
        id (str): Unique user identifier (subject from OAuth)
        name (str): User's display name
        email (str): User's email address
    """

    def __init__(self, sub, name=None, email=None):
        """
        Initialize a new User instance.
        
        Args:
            sub (str): The unique subject identifier from OAuth provider
            name (str, optional): User's display name
            email (str, optional): User's email address
        """

        self.id = sub
        self.name = name
        self.email = email

@login_mgr.user_loader
def load_user(user_id):
    """
    Load a user from the session for Flask-Login.
    
    This callback is used by Flask-Login to reload the user object from
    the user ID stored in the session. It checks the session for user
    information and creates a User object if valid data is found.
        
    Note:
        This function is called on every request for authenticated users
        to reconstruct the user object from session data.
    """

    info = session.get('user')
    if info and info.get('sub') == user_id:
        return User(info['sub'], info.get('name'), info.get('email'))
    return None
