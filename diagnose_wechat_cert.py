#!/usr/bin/env python
"""
微信支付证书问题诊断脚本

检查商户证书、私钥和签名是否正确
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# 加载 .env 文件
env_path = Path(__file__).parent / 'django_shop' / '.env'
if env_path.exists():
    load_dotenv(env_path)

WECHAT_MCH_ID = os.environ.get('WECHAT_MCH_ID', '')
WECHAT_SERIAL_NO = os.environ.get('WECHAT_SERIAL_NO', '')
WECHAT_API_V3_KEY = os.environ.get('WECHAT_API_V3_KEY', '')
WECHAT_PRIVATE_KEY = os.environ.get('WECHAT_PRIVATE_KEY', '')

print("=" * 80)
print("微信支付证书诊断工具")
print("=" * 80)

# 1. 检查私钥格式
print("\n【1】检查私钥格式")
try:
    private_key = serialization.load_pem_private_key(
        WECHAT_PRIVATE_KEY.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    print("  ✅ 私钥格式正确")
    print(f"  密钥类型: {type(private_key).__name__}")
    print(f"  密钥长度: {private_key.key_size} bits")
except Exception as e:
    print(f"  ❌ 私钥格式错误: {e}")
    exit(1)

# 2. 检查证书序列号长度和格式
print("\n【2】检查证书序列号")
print(f"  序列号: {WECHAT_SERIAL_NO}")
print(f"  长度: {len(WECHAT_SERIAL_NO)} 字符")
if len(WECHAT_SERIAL_NO) == 40:
    print("  ✅ 序列号长度正确（40位十六进制）")
else:
    print(f"  ⚠️  序列号长度异常（应为40位，实际{len(WECHAT_SERIAL_NO)}位）")

# 3. 检查 APIv3 密钥
print("\n【3】检查 APIv3 密钥")
print(f"  密钥长度: {len(WECHAT_API_V3_KEY)} 字符")
if len(WECHAT_API_V3_KEY) == 32:
    print("  ✅ APIv3密钥长度正确（32字符）")
else:
    print(f"  ⚠️  APIv3密钥长度异常（应为32字符，实际{len(WECHAT_API_V3_KEY)}字符）")

# 4. 测试签名功能
print("\n【4】测试签名功能")
try:
    test_data = "test signature"
    signature = private_key.sign(
        test_data.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    print("  ✅ 签名功能正常")
    print(f"  测试签名（Base64）: {signature_b64[:50]}...")
except Exception as e:
    print(f"  ❌ 签名失败: {e}")
    exit(1)

# 5. 尝试提取私钥对应的公钥（用于验证）
print("\n【5】提取公钥信息")
try:
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("  ✅ 成功提取公钥")
    print("  公钥（前50字符）:")
    print(f"  {public_pem.decode('utf-8')[:100]}...")
except Exception as e:
    print(f"  ❌ 提取公钥失败: {e}")

# 6. 检查是否有商户公钥证书文件
print("\n【6】查找商户证书文件")
possible_cert_paths = [
    f'/Users/xiaoxiao/Downloads/apiclient_cert.pem',
    f'/Users/xiaoxiao/Downloads/pubkey_{WECHAT_SERIAL_NO}.pem',
    Path(__file__).parent / 'django_shop' / f'apiclient_cert.pem',
]

cert_found = False
for cert_path in possible_cert_paths:
    if os.path.exists(cert_path):
        print(f"  ✅ 找到证书文件: {cert_path}")
        cert_found = True

        # 尝试读取证书
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()

            # 尝试解析为 X.509 证书
            try:
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                print(f"  证书类型: X.509 证书")
                print(f"  证书序列号: {hex(cert.serial_number)[2:].upper()}")
                print(f"  主题: {cert.subject}")
                print(f"  颁发者: {cert.issuer}")
                print(f"  有效期: {cert.not_valid_before_utc} 至 {cert.not_valid_after_utc}")

                # 验证序列号是否匹配
                cert_serial = hex(cert.serial_number)[2:].upper()
                if cert_serial == WECHAT_SERIAL_NO:
                    print(f"  ✅ 证书序列号与配置匹配")
                else:
                    print(f"  ⚠️  证书序列号不匹配:")
                    print(f"      配置: {WECHAT_SERIAL_NO}")
                    print(f"      证书: {cert_serial}")

            except Exception as e:
                print(f"  ℹ️  不是 X.509 证书格式，可能是公钥文件")
                # 尝试作为公钥读取
                try:
                    pub_key = serialization.load_pem_public_key(cert_data, default_backend())
                    print(f"  证书类型: RSA 公钥")
                except:
                    print(f"  ⚠️  无法识别文件格式")

        except Exception as e:
            print(f"  ❌ 读取证书文件失败: {e}")

if not cert_found:
    print("  ⚠️  未找到商户证书文件")
    print("  提示：商户证书文件通常命名为 apiclient_cert.pem 或 pubkey_序列号.pem")

print("\n" + "=" * 80)
print("诊断建议")
print("=" * 80)

print("""
根据诊断结果，可能的问题和解决方案：

1. 如果私钥和签名功能正常，但仍无法下载平台证书：
   - 可能是微信服务器暂时不可用或网络问题
   - 可以尝试使用测试模式来绕过证书验证（仅用于开发）

2. 关于微信支付平台证书：
   - 微信支付平台证书通常由 wechatpayv3 库自动从微信服务器下载
   - 首次初始化时会调用 /v3/certificates API 下载平台证书
   - 如果 API 返回 404，可能是签名问题或权限问题

3. 临时解决方案：
   - 方案A：使用支付测试模式（跳过真实支付）
   - 方案B：联系微信支付技术支持确认平台证书下载权限
   - 方案C：使用旧版 V2 API（不推荐，V2 已逐步废弃）

4. 下一步建议：
   - 确认商户号是否完成了实名认证
   - 确认 Native 支付产品是否已完全激活
   - 检查商户号是否有欠费或限制状态
""")

print("\n是否要尝试使用测试模式？(y/n): ", end='')
