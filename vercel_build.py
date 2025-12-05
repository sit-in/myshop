#!/usr/bin/env python3
"""
Vercel build script for Django.
This script is automatically executed by Vercel during the build phase.
"""
import os
import sys
import subprocess

# Add django_shop to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django_shop'))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Change to django_shop directory
os.chdir('django_shop')

# Collect static files
print("Collecting static files...")
subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)

print("Build completed successfully!")
