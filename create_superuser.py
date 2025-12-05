#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 检查是否已存在 admin 用户
if User.objects.filter(username='admin').exists():
    print("✓ 超级用户 'admin' 已存在")
    user = User.objects.get(username='admin')
    print(f"  用户名: {user.username}")
    print(f"  邮箱: {user.email}")
    print(f"  是否为超级用户: {user.is_superuser}")
else:
    # 创建新的超级用户
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123456'
    )
    print("✓ 超级用户创建成功！")
    print(f"  用户名: admin")
    print(f"  密码: admin123456")
    print(f"  邮箱: admin@example.com")
    print("\n⚠️  请在登录后立即修改密码！")
