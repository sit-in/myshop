#!/bin/bash

# Vercel build script - runs during deployment
echo "========================================="
echo "Starting Django build process..."
echo "========================================="

# Navigate to Django project directory
cd django_shop

# Note: Database migrations should be run manually in Supabase SQL Editor
# Vercel build environment cannot access production database
echo "⚠️  Note: Please run database migrations manually in Supabase"
echo "   Visit: https://supabase.com/dashboard → SQL Editor"
echo "   Execute: ALTER TABLE shop_order ADD COLUMN quantity INTEGER NOT NULL DEFAULT 1;"

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

# Check if collectstatic succeeded
if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully!"
    echo "Static files location: $(pwd)/staticfiles"
    ls -la staticfiles/ | head -10
else
    echo "❌ Failed to collect static files"
    exit 1
fi

echo "========================================="
echo "Build process completed!"
echo "========================================="
