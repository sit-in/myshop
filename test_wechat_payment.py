#!/usr/bin/env python
"""
测试微信支付配置

运行此脚本来验证微信支付配置是否正确
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django_shop'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.wechat_pay import WeChatPayClient

def test_wechat_pay_init():
    """测试微信支付客户端初始化"""
    print("\n" + "=" * 80)
    print("微信支付配置测试")
    print("=" * 80)

    try:
        # 尝试初始化微信支付客户端
        client = WeChatPayClient()

        print("\n" + "=" * 80)
        print("✅ 测试通过！")
        print("=" * 80)
        print("\n微信支付配置正确，客户端初始化成功。")
        print("\n下一步操作：")
        print("1. 将 .env 文件中的配置同步到 Vercel 环境变量")
        print("2. 特别注意添加以下两个新的环境变量：")
        print("   - WECHAT_PLATFORM_CERT")
        print("   - WECHAT_PLATFORM_CERT_SERIAL_NO")
        print("3. 重新部署应用到 Vercel")

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ 测试失败！")
        print("=" * 80)
        print(f"\n错误信息: {e}")
        print("\n请检查以下配置：")
        print("1. 商户号 (WECHAT_MCH_ID)")
        print("2. 商户证书序列号 (WECHAT_SERIAL_NO)")
        print("3. 商户私钥 (WECHAT_PRIVATE_KEY)")
        print("4. APIv3密钥 (WECHAT_API_V3_KEY)")
        print("5. 平台证书 (WECHAT_PLATFORM_CERT)")
        print("6. 平台证书序列号 (WECHAT_PLATFORM_CERT_SERIAL_NO)")

        return False

if __name__ == '__main__':
    success = test_wechat_pay_init()
    sys.exit(0 if success else 1)
