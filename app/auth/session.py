"""
OAuth token validation and session management.

Provides token validation using multiple strategies: expiration checks,
userinfo endpoint validation, and OAuth token introspection. Includes
caching mechanisms to minimize API calls to the OAuth provider.
"""

from datetime import datetime, timedelta
from flask import session, current_app
import requests

def validate_oauth_session():
    """
    OAuth session validation

    Uses multiple validation strategies in order of preference:
    1. Token expiration
    2. Userinfo endpoint validation
    3. Token introspection
    """

    access_token = session.get('access_token')

    if not access_token:
        return False

    if not is_token_expired():
        return True

    if validate_with_userinfo(access_token):
        return True

    if validate_with_introspection(access_token):
        return True

    # All validation methods failed
    return False

def is_token_expired():
    """
    Check if stored token has expired based on expires_at timestamp
    """

    token_expires_at = session.get('token_expires_at')

    if not token_expires_at:
        # No expiration info - assume expired
        return True

    if isinstance(token_expires_at, str):
        token_expires_at = datetime.fromisoformat(token_expires_at)

    # Add a 1 minute buffer for potential network delays
    return datetime.utcnow() >= token_expires_at - timedelta(minutes=1)

def validate_with_userinfo(access_token):
    """
    Validate token using OIDC userinfo endpoint
    """

    try:
        userinfo_endpoint = get_endpoint_from_metadata('userinfo_endpoint')

        if not userinfo_endpoint:
            return False

        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_endpoint, headers=headers, timeout=5)

        if response.status_code == 200:
            # Token is valid - store validation timestamp
            session['last_token_validation'] = datetime.utcnow().isoformat()
            return True

        return False

    except (requests.RequestException, ValueError, KeyError) as error:
        current_app.logger.warning('Userinfo validation failed: %s', error)
        return False

def validate_with_introspection(access_token):
    """
    Validate token using OAuth 2.0 token introspection
    """

    try:
        introspection_endpoint = get_endpoint_from_metadata('introspection_endpoint')
        if not introspection_endpoint:
            return False

        data = {
            'token': access_token,
            'client_id': current_app.config.get('OAUTH_CLIENT_ID'),
            'client_secret': current_app.config.get('OAUTH_CLIENT_SECRET')
        }

        response = requests.post(introspection_endpoint, data=data, timeout=5)

        if response.status_code == 200:
            result = response.json()
            is_active = result.get('active', False)

            if is_active:
                # Update expiration info if provided
                exp = result.get('exp')
                if exp:
                    expires_at = datetime.utcfromtimestamp(exp)
                    session['token_expires_at'] = expires_at.isoformat()

                session['last_token_validation'] = datetime.utcnow().isoformat()
                return True

        return False

    except (requests.RequestException, ValueError, KeyError) as error:
        current_app.logger.debug(
            'Token introspection not available or failed: %s', error)
        return False

def get_endpoint_from_metadata(endpoint_name):
    """
    Get endpoint URL from OIDC discovery metadata
    """

    try:
        metadata_url = current_app.config.get('OAUTH_METADATA_URL')
        if not metadata_url:
            return None

        # Cache metadata for a short time to avoid repeated requests
        cache_key = 'oauth_metadata'
        cached_metadata = session.get(cache_key)
        cached_time = session.get(f'{cache_key}_time')

        # Use cached metadata if less than 5 minutes old
        if cached_metadata and cached_time:
            cache_age = datetime.utcnow() - datetime.fromisoformat(cached_time)
            if cache_age < timedelta(minutes=5):
                return cached_metadata.get(endpoint_name)

        # Fetch fresh metadata
        response = requests.get(metadata_url, timeout=5)
        if response.status_code == 200:
            metadata = response.json()

            # Cache metadata
            session[cache_key] = metadata
            session[f'{cache_key}_time'] = datetime.utcnow().isoformat()

            return metadata.get(endpoint_name)

    except (requests.RequestException, ValueError, KeyError) as error:
        current_app.logger.warning(
            'Failed to get %s from metadata: %s', endpoint_name, error)
        return None

    return None

def should_validate_token():
    """
    Determine if token validation should be performed

    Only validate periodically to avoid excessive API calls
    """

    last_validation = session.get('last_token_validation')
    if not last_validation:
        return True

    # Validate every 5 minutes
    validation_interval = current_app.config.get('TOKEN_VALIDATION_INTERVAL_MINUTES', 5)
    last_validation_time = datetime.fromisoformat(last_validation)

    return datetime.utcnow() - last_validation_time > timedelta(minutes=validation_interval)
