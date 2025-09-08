"""
WSGI entry point

Creates the Flask app instance for production deployment with Gunicorn
"""
# pylint: disable=wrong-import-position
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()
