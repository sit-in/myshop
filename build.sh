#!/bin/bash

# Vercel build script for Django
cd django_shop

# Collect static files
python3 manage.py collectstatic --noinput

echo "Build completed successfully!"
