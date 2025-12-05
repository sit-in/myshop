"""
WSGI entrypoint for Vercel deployment.
This file adds the django_shop directory to the Python path
and imports the actual WSGI application.
"""
import os
import sys

# Add the django_shop directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django_shop'))

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
