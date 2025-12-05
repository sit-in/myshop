"""
WSGI entrypoint for Vercel deployment.
This file adds the django_shop directory to the Python path
and imports the actual WSGI application.
"""
import os
import sys

# Add the django_shop directory to the Python path
project_dir = os.path.join(os.path.dirname(__file__), 'django_shop')
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import the WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log error for debugging in Vercel logs
    print(f"ERROR: Failed to initialize WSGI application: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Environment variables: DATABASE_URL={'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}")
    raise
