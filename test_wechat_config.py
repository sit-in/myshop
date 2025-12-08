#!/usr/bin/env python3
"""测试微信支付配置是否正确"""

import os
import sys
import django

# 添加 Django 项目路径
sys.path.insert(0, '/Users/xiaoxiao/Desktop/AI_coding/myshop_git/myshop/django_shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("微信支付配置验证")
print("=" * 60)

# 检查商户号
mch_id = settings.WECHAT_MCH_ID
print(f"\n1. 商户号 (WECHAT_MCH_ID):")
print(f"   值: {mch_id}")
print(f"   长度: {len(mch_id)} 字符")
print(f"   ✅ 正确" if mch_id.isdigit() and len(mch_id) == 10 else "   ❌ 错误：应为10位纯数字")

# 检查 AppID
app_id = settings.WECHAT_APP_ID
print(f"\n2. AppID (WECHAT_APP_ID):")
print(f"   值: {app_id}")
print(f"   长度: {len(app_id)} 字符")
print(f"   ✅ 正确" if app_id.startswith('wx') and len(app_id) == 18 else "   ❌ 错误：应以wx开头，共18字符")

# 检查证书序列号
serial_no = settings.WECHAT_SERIAL_NO
print(f"\n3. 证书序列号 (WECHAT_SERIAL_NO):")
print(f"   值: {serial_no[:8]}...{serial_no[-8:] if len(serial_no) > 16 else ''}")
print(f"   长度: {len(serial_no)} 字符")
print(f"   ✅ 正确" if len(serial_no) == 40 else "   ❌ 错误：应为40位十六进制")

# 检查 APIv3 密钥
api_v3_key = settings.WECHAT_API_V3_KEY
print(f"\n4. APIv3密钥 (WECHAT_API_V3_KEY):")
print(f"   长度: {len(api_v3_key)} 字符")
print(f"   ✅ 正确" if len(api_v3_key) == 32 else f"   ❌ 错误：应为32字符，当前{len(api_v3_key)}字符")

# 检查私钥
private_key = settings.WECHAT_PRIVATE_KEY
print(f"\n5. 私钥 (WECHAT_PRIVATE_KEY):")
print(f"   长度: {len(private_key)} 字符")
has_begin = '-----BEGIN PRIVATE KEY-----' in private_key
has_end = '-----END PRIVATE KEY-----' in private_key
has_newline = '\\n' in private_key or '\n' in private_key
print(f"   包含 BEGIN: {'✅' if has_begin else '❌'}")
print(f"   包含 END: {'✅' if has_end else '❌'}")
print(f"   包含换行符: {'✅' if has_newline else '⚠️  可能缺少换行符'}")
print(f"   {'✅ 格式正确' if (has_begin and has_end) else '❌ 格式错误'}")

# 检查回调 URL
notify_url = settings.WECHAT_PAY_NOTIFY_URL
print(f"\n6. 支付回调URL (WECHAT_PAY_NOTIFY_URL):")
print(f"   值: {notify_url}")
print(f"   ✅ 正确" if notify_url.startswith('https://') else "   ❌ 错误：应使用 https://")

print("\n" + "=" * 60)

# 尝试初始化微信支付客户端
print("\n尝试初始化微信支付客户端...")
try:
    from shop.wechat_pay import WeChatPayClient
    client = WeChatPayClient()
    print("✅ 初始化成功！配置正确。")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
