#!/usr/bin/env python
"""
下载微信支付平台证书

使用方法：
1. 确保已安装 wechatpayv3: pip install wechatpayv3
2. 设置环境变量或在下方填写你的配置
3. 运行此脚本: python download_wechat_platform_cert.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from wechatpayv3 import WeChatPay, WeChatPayType

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载配置文件: {env_path}")
else:
    # 尝试从 django_shop 目录加载
    env_path = Path(__file__).parent / 'django_shop' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载配置文件: {env_path}")
    else:
        print("⚠️  未找到 .env 文件，将使用环境变量")

# 从环境变量读取配置（或在下方直接填写）
WECHAT_MCH_ID = os.environ.get('WECHAT_MCH_ID', '')  # 商户号
WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', '')  # AppID
WECHAT_SERIAL_NO = os.environ.get('WECHAT_SERIAL_NO', '')  # 商户证书序列号
WECHAT_API_V3_KEY = os.environ.get('WECHAT_API_V3_KEY', '')  # APIv3密钥
WECHAT_PRIVATE_KEY = os.environ.get('WECHAT_PRIVATE_KEY', '')  # 商户私钥

def download_platform_certificate():
    """下载微信支付平台证书"""

    # 检查配置
    if not all([WECHAT_MCH_ID, WECHAT_APP_ID, WECHAT_SERIAL_NO, WECHAT_API_V3_KEY, WECHAT_PRIVATE_KEY]):
        print("❌ 错误：缺少必要的配置参数")
        print("\n请设置以下环境变量：")
        print("  - WECHAT_MCH_ID: 商户号")
        print("  - WECHAT_APP_ID: AppID")
        print("  - WECHAT_SERIAL_NO: 商户证书序列号")
        print("  - WECHAT_API_V3_KEY: APIv3密钥")
        print("  - WECHAT_PRIVATE_KEY: 商户私钥")
        return

    print("=" * 80)
    print("微信支付平台证书下载工具")
    print("=" * 80)
    print(f"商户号: {WECHAT_MCH_ID}")
    print(f"AppID: {WECHAT_APP_ID}")
    print(f"证书序列号: {WECHAT_SERIAL_NO[:8]}...{WECHAT_SERIAL_NO[-8:]}")
    print(f"APIv3密钥长度: {len(WECHAT_API_V3_KEY)} 字符")
    print(f"私钥格式: {'✅ 正确' if 'BEGIN PRIVATE KEY' in WECHAT_PRIVATE_KEY else '❌ 错误'}")
    print("=" * 80)

    try:
        print("\n正在初始化微信支付客户端...")
        wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=WECHAT_MCH_ID,
            private_key=WECHAT_PRIVATE_KEY,
            cert_serial_no=WECHAT_SERIAL_NO,
            apiv3_key=WECHAT_API_V3_KEY,
            appid=WECHAT_APP_ID,
        )
        print("✅ 客户端初始化成功")

        print("\n正在获取平台证书列表...")
        # 获取平台证书
        # wechatpayv3 库会自动下载和管理证书
        # 我们需要直接访问证书 API
        from wechatpayv3.core import Core

        # 创建 Core 实例
        core = Core(
            mchid=WECHAT_MCH_ID,
            cert_serial_no=WECHAT_SERIAL_NO,
            private_key=WECHAT_PRIVATE_KEY,
            apiv3_key=WECHAT_API_V3_KEY
        )

        # 下载证书
        print("✅ 正在下载证书...")
        certs = core._download_certificates()

        if not certs:
            print("❌ 未能获取到平台证书")
            return

        print(f"\n✅ 成功获取 {len(certs)} 个平台证书")
        print("=" * 80)

        for idx, cert_info in enumerate(certs, 1):
            print(f"\n【证书 {idx}】")
            print(f"序列号: {cert_info.get('serial_no', 'N/A')}")
            print(f"生效时间: {cert_info.get('effective_time', 'N/A')}")
            print(f"过期时间: {cert_info.get('expire_time', 'N/A')}")

            # 获取证书内容
            cert_content = cert_info.get('encrypt_certificate', {}).get('ciphertext', '')

            if cert_content:
                # 证书已经是解密后的 PEM 格式
                # 如果是密文，需要解密
                try:
                    from wechatpayv3.utils import aes_decrypt
                    nonce = cert_info.get('encrypt_certificate', {}).get('nonce', '')
                    associated_data = cert_info.get('encrypt_certificate', {}).get('associated_data', '')

                    # 解密证书
                    decrypted_cert = aes_decrypt(
                        nonce=nonce,
                        ciphertext=cert_content,
                        associated_data=associated_data,
                        apiv3_key=WECHAT_API_V3_KEY
                    )

                    print("\n证书内容（PEM 格式）：")
                    print("-" * 80)
                    print(decrypted_cert)
                    print("-" * 80)

                    # 保存证书到文件
                    cert_filename = f"wechat_platform_cert_{cert_info.get('serial_no', idx)}.pem"
                    with open(cert_filename, 'w', encoding='utf-8') as f:
                        f.write(decrypted_cert)
                    print(f"\n✅ 证书已保存到: {cert_filename}")

                    print("\n📋 配置到 Vercel 环境变量：")
                    print("=" * 80)
                    print("变量名: WECHAT_PLATFORM_CERT")
                    print("变量值:")
                    print(decrypted_cert)
                    print("=" * 80)

                except Exception as decrypt_error:
                    print(f"❌ 解密证书失败: {decrypt_error}")
            else:
                print("⚠️  证书内容为空")

        print("\n" + "=" * 80)
        print("✅ 下载完成！")
        print("=" * 80)
        print("\n下一步操作：")
        print("1. 复制上面的证书内容（包括 -----BEGIN CERTIFICATE----- 和 -----END CERTIFICATE-----）")
        print("2. 在 Vercel 项目设置中添加环境变量 WECHAT_PLATFORM_CERT")
        print("3. 粘贴证书内容作为变量值")
        print("4. 重新部署你的应用")

    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n可能的原因：")
        print("1. 商户证书序列号不正确")
        print("2. 商户私钥格式错误或不匹配")
        print("3. APIv3密钥不正确")
        print("4. 网络连接问题")

if __name__ == '__main__':
    download_platform_certificate()
