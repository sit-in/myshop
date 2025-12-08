#!/usr/bin/env python
"""
Vercel 迁移脚本 - 手动执行数据库迁移
用法: python migrate.py
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("=" * 50)
    print("正在执行数据库迁移...")
    print("=" * 50)

    try:
        # 执行迁移
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("\n✅ 迁移执行成功！")

        # 显示迁移状态
        print("\n当前迁移状态：")
        execute_from_command_line(['manage.py', 'showmigrations'])

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        sys.exit(1)
