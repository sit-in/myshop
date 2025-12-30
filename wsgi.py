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

    # Log initialization info
    database_url = os.environ.get('DATABASE_URL', '')
    print(f"[INIT] Initializing Django WSGI application...")
    print(f"[INIT] DATABASE_URL: {'SET (length: ' + str(len(database_url)) + ')' if database_url else 'NOT SET'}")
    print(f"[INIT] DEBUG: {os.environ.get('DEBUG', 'not set')}")

    # Log database URL details (safely, without exposing password)
    if database_url:
        # Parse URL to show structure
        import re
        url_pattern = r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)'
        match = re.match(url_pattern, database_url)
        if match:
            user, password, host, db = match.groups()
            print(f"[INIT] DB User: {user}")
            print(f"[INIT] DB Host: {host}")
            print(f"[INIT] DB Name: {db}")
            print(f"[INIT] Password length: {len(password)}")
        else:
            print(f"[INIT] WARNING: DATABASE_URL format may be incorrect")

    application = get_wsgi_application()

    # Vercel requires the variable to be named 'app' or 'handler'
    app = application

    # Debug: Print middleware configuration
    from django.conf import settings
    print(f"[INIT] MIDDLEWARE configuration:")
    for i, middleware in enumerate(settings.MIDDLEWARE, 1):
        print(f"[INIT]   {i}. {middleware}")

    # Check if BasicAuthMiddleware is in the list
    basic_auth_enabled = any('BasicAuthMiddleware' in m for m in settings.MIDDLEWARE)
    print(f"[INIT] BasicAuthMiddleware in MIDDLEWARE: {basic_auth_enabled}")

    # Check environment variables
    print(f"[INIT] BASIC_AUTH_ENABLED env: {os.environ.get('BASIC_AUTH_ENABLED', 'NOT_SET')}")
    print(f"[INIT] BASIC_AUTH_USERNAME env: {'SET' if os.environ.get('BASIC_AUTH_USERNAME') else 'NOT_SET'}")
    print(f"[INIT] BASIC_AUTH_PASSWORD env: {'SET' if os.environ.get('BASIC_AUTH_PASSWORD') else 'NOT_SET'}")

    print(f"[INIT] ✅ WSGI application initialized successfully")

except Exception as e:
    # Log detailed error for debugging in Vercel logs
    print(f"[ERROR] ❌ Failed to initialize WSGI application")
    print(f"[ERROR] Exception type: {type(e).__name__}")
    print(f"[ERROR] Exception message: {str(e)}")
    print(f"[ERROR] Python path: {sys.path}")
    print(f"[ERROR] Current directory: {os.getcwd()}")

    import traceback
    print(f"[ERROR] Full traceback:")
    traceback.print_exc()

    raise
