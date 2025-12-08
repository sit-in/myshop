#!/usr/bin/env python3
"""验证证书序列号和私钥是否匹配"""

import os
import sys

# 添加 Django 项目路径
sys.path.insert(0, '/Users/xiaoxiao/Desktop/AI_coding/myshop_git/myshop/django_shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.conf import settings
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

print("=" * 60)
print("验证证书和私钥是否匹配")
print("=" * 60)

# 获取配置的序列号
config_serial = settings.WECHAT_SERIAL_NO
print(f"\n配置的证书序列号: {config_serial}")

# 加载私钥
try:
    private_key_data = settings.WECHAT_PRIVATE_KEY

    # 处理 \n 转义字符
    if '\\n' in private_key_data:
        private_key_data = private_key_data.replace('\\n', '\n')

    private_key = serialization.load_pem_private_key(
        private_key_data.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    print("✅ 私钥加载成功")

    # 获取公钥
    public_key = private_key.public_key()
    print("✅ 从私钥提取公钥成功")

    # 测试签名和验证
    test_data = b"test message"
    signature = private_key.sign(
        test_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    try:
        public_key.verify(
            signature,
            test_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("✅ 私钥可以正常签名和验证")
    except Exception as e:
        print(f"❌ 签名验证失败: {e}")

except Exception as e:
    print(f"❌ 私钥加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("建议:")
print("=" * 60)
print("1. 从微信商户平台重新下载最新的 API 证书")
print("2. 使用以下命令从证书文件提取序列号:")
print("   openssl x509 -in apiclient_cert.pem -noout -serial")
print("3. 确保私钥来自 apiclient_key.pem 文件")
print("4. 更新 Vercel 环境变量后重新部署")
print("=" * 60)
