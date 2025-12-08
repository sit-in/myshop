#!/usr/bin/env python
"""
直接调用微信支付 API 下载平台证书

这个脚本绕过 wechatpayv3 库，直接调用微信支付的证书接口
"""

import os
import json
import time
import base64
from pathlib import Path
from dotenv import load_dotenv
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 加载 .env 文件
env_path = Path(__file__).parent / 'django_shop' / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载配置文件: {env_path}")
else:
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载配置文件: {env_path}")

# 从环境变量读取配置
WECHAT_MCH_ID = os.environ.get('WECHAT_MCH_ID', '')
WECHAT_SERIAL_NO = os.environ.get('WECHAT_SERIAL_NO', '')
WECHAT_API_V3_KEY = os.environ.get('WECHAT_API_V3_KEY', '')
WECHAT_PRIVATE_KEY = os.environ.get('WECHAT_PRIVATE_KEY', '')

def generate_signature(method, url_path, timestamp, nonce, body=''):
    """生成请求签名"""
    # 构建待签名字符串
    sign_str = f"{method}\n{url_path}\n{timestamp}\n{nonce}\n{body}\n"

    # 加载私钥
    private_key = serialization.load_pem_private_key(
        WECHAT_PRIVATE_KEY.encode('utf-8'),
        password=None,
        backend=default_backend()
    )

    # 使用 SHA256withRSA 签名
    signature = private_key.sign(
        sign_str.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Base64 编码
    return base64.b64encode(signature).decode('utf-8')

def build_authorization_header(method, url_path, timestamp, nonce, body=''):
    """构建 Authorization 头"""
    signature = generate_signature(method, url_path, timestamp, nonce, body)

    auth_str = (
        f'WECHATPAY2-SHA256-RSA2048 '
        f'mchid="{WECHAT_MCH_ID}",'
        f'nonce_str="{nonce}",'
        f'signature="{signature}",'
        f'timestamp="{timestamp}",'
        f'serial_no="{WECHAT_SERIAL_NO}"'
    )

    return auth_str

def decrypt_certificate(nonce, ciphertext, associated_data, apiv3_key):
    """解密证书内容"""
    # Base64 解码密文
    ciphertext_bytes = base64.b64decode(ciphertext)

    # 使用 AESGCM 解密
    aesgcm = AESGCM(apiv3_key.encode('utf-8'))

    try:
        plaintext = aesgcm.decrypt(
            nonce.encode('utf-8'),
            ciphertext_bytes,
            associated_data.encode('utf-8') if associated_data else None
        )
        return plaintext.decode('utf-8')
    except Exception as e:
        print(f"❌ 解密失败: {e}")
        return None

def download_certificates():
    """下载平台证书"""
    print("=" * 80)
    print("微信支付平台证书下载工具（直接 API 调用）")
    print("=" * 80)
    print(f"商户号: {WECHAT_MCH_ID}")
    print(f"证书序列号: {WECHAT_SERIAL_NO[:8]}...{WECHAT_SERIAL_NO[-8:]}")
    print(f"APIv3密钥长度: {len(WECHAT_API_V3_KEY)} 字符")
    print(f"私钥格式: {'✅ 正确' if 'BEGIN PRIVATE KEY' in WECHAT_PRIVATE_KEY else '❌ 错误'}")
    print("=" * 80)

    # 证书接口
    url = "https://api.mch.weixin.qq.com/v3/certificates"
    url_path = "/v3/certificates"
    method = "GET"

    # 生成时间戳和随机数
    timestamp = str(int(time.time()))
    nonce = os.urandom(16).hex()

    print(f"\n请求参数:")
    print(f"  URL: {url}")
    print(f"  时间戳: {timestamp}")
    print(f"  随机数: {nonce}")

    # 构建请求头
    headers = {
        'Authorization': build_authorization_header(method, url_path, timestamp, nonce),
        'Accept': 'application/json',
        'User-Agent': 'python-wechatpay-cert-downloader'
    }

    print(f"\n正在请求证书 API...")

    try:
        response = requests.get(url, headers=headers, timeout=30)

        print(f"  响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if 'data' not in data or not data['data']:
                print("❌ 响应中没有证书数据")
                print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return

            certs = data['data']
            print(f"\n✅ 成功获取 {len(certs)} 个平台证书")
            print("=" * 80)

            for idx, cert_info in enumerate(certs, 1):
                print(f"\n【证书 {idx}】")
                serial_no = cert_info.get('serial_no', 'N/A')
                effective_time = cert_info.get('effective_time', 'N/A')
                expire_time = cert_info.get('expire_time', 'N/A')

                print(f"序列号: {serial_no}")
                print(f"生效时间: {effective_time}")
                print(f"过期时间: {expire_time}")

                # 解密证书
                encrypt_cert = cert_info.get('encrypt_certificate', {})
                nonce = encrypt_cert.get('nonce', '')
                ciphertext = encrypt_cert.get('ciphertext', '')
                associated_data = encrypt_cert.get('associated_data', '')

                if ciphertext:
                    print("\n正在解密证书...")
                    decrypted_cert = decrypt_certificate(
                        nonce,
                        ciphertext,
                        associated_data,
                        WECHAT_API_V3_KEY
                    )

                    if decrypted_cert:
                        print("✅ 证书解密成功")
                        print("\n证书内容（PEM 格式）：")
                        print("-" * 80)
                        print(decrypted_cert)
                        print("-" * 80)

                        # 保存证书到文件
                        cert_filename = f"wechat_platform_cert_{serial_no}.pem"
                        with open(cert_filename, 'w', encoding='utf-8') as f:
                            f.write(decrypted_cert)
                        print(f"\n✅ 证书已保存到: {cert_filename}")

                        print("\n" + "=" * 80)
                        print("📋 配置到 Vercel 环境变量")
                        print("=" * 80)
                        print("变量名: WECHAT_PLATFORM_CERT")
                        print("\n变量值（复制下面的内容）:")
                        print(decrypted_cert)
                        print("=" * 80)
                    else:
                        print("❌ 证书解密失败")
                else:
                    print("⚠️  证书密文为空")

            print("\n" + "=" * 80)
            print("✅ 下载完成！")
            print("=" * 80)
            print("\n下一步操作：")
            print("1. 复制上面的证书内容（包括 -----BEGIN CERTIFICATE----- 和 -----END CERTIFICATE-----）")
            print("2. 在 Vercel 项目设置中添加环境变量 WECHAT_PLATFORM_CERT")
            print("3. 粘贴证书内容作为变量值")
            print("4. 重新部署你的应用")

        elif response.status_code == 401:
            print("❌ 认证失败 (401)")
            print("可能的原因：")
            print("  1. 商户证书序列号不正确")
            print("  2. 商户私钥与证书不匹配")
            print("  3. 签名算法错误")
            print(f"\n响应内容: {response.text}")
        elif response.status_code == 403:
            print("❌ 权限不足 (403)")
            print("可能的原因：商户号未开通相关权限")
            print(f"\n响应内容: {response.text}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 检查配置
    if not all([WECHAT_MCH_ID, WECHAT_SERIAL_NO, WECHAT_API_V3_KEY, WECHAT_PRIVATE_KEY]):
        print("❌ 错误：缺少必要的配置参数")
        print("\n请在 .env 文件中配置：")
        print("  - WECHAT_MCH_ID: 商户号")
        print("  - WECHAT_SERIAL_NO: 商户证书序列号")
        print("  - WECHAT_API_V3_KEY: APIv3密钥")
        print("  - WECHAT_PRIVATE_KEY: 商户私钥")
    else:
        download_certificates()
