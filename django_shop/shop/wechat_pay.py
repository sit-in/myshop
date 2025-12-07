"""微信支付工具类 - 使用微信支付 V3 API"""
import os
import time
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from wechatpayv3 import WeChatPay, WeChatPayType


class WeChatPayClient:
    """微信支付客户端 - 使用微信支付 V3 API"""

    def __init__(self):
        """初始化微信支付客户端"""
        # 创建证书缓存目录
        # Vercel Serverless 环境只有 /tmp 可写
        cert_dir = '/tmp/wechatpay_certs' if os.environ.get('VERCEL') else os.path.join(settings.BASE_DIR, 'wechatpay_certs')
        os.makedirs(cert_dir, exist_ok=True)

        # 打印配置信息（脱敏）用于调试
        print("=" * 60)
        print("微信支付初始化配置检查:")
        print(f"  商户号 (mchid): {settings.WECHAT_MCH_ID}")
        print(f"  AppID: {settings.WECHAT_APP_ID}")
        print(f"  证书序列号: {settings.WECHAT_SERIAL_NO[:8]}...{settings.WECHAT_SERIAL_NO[-8:] if len(settings.WECHAT_SERIAL_NO) > 16 else ''}")
        print(f"  APIv3密钥长度: {len(settings.WECHAT_API_V3_KEY)} 字符")
        print(f"  私钥格式: {'✅ 包含 BEGIN PRIVATE KEY' if 'BEGIN PRIVATE KEY' in settings.WECHAT_PRIVATE_KEY else '❌ 格式错误'}")
        print(f"  平台证书: {'✅ 已配置' if settings.WECHAT_PLATFORM_CERT else '⚠️  未配置'}")
        if settings.WECHAT_PLATFORM_CERT:
            print(f"  平台证书序列号: {settings.WECHAT_PLATFORM_CERT_SERIAL_NO[:8]}...{settings.WECHAT_PLATFORM_CERT_SERIAL_NO[-8:] if len(settings.WECHAT_PLATFORM_CERT_SERIAL_NO) > 16 else ''}")
        print(f"  证书目录: {cert_dir}")
        print(f"  回调 URL: {settings.WECHAT_PAY_NOTIFY_URL}")
        print("=" * 60)

        try:
            print("\n正在初始化微信支付客户端...")

            # 准备基础初始化参数
            init_params = {
                'wechatpay_type': WeChatPayType.NATIVE,
                'mchid': settings.WECHAT_MCH_ID,
                'private_key': settings.WECHAT_PRIVATE_KEY,
                'cert_serial_no': settings.WECHAT_SERIAL_NO,
                'apiv3_key': settings.WECHAT_API_V3_KEY,
                'appid': settings.WECHAT_APP_ID,
                'notify_url': settings.WECHAT_PAY_NOTIFY_URL,
            }

            # 如果配置了平台公钥，使用公钥模式（新商户号）
            if settings.WECHAT_PLATFORM_CERT and settings.WECHAT_PLATFORM_CERT_SERIAL_NO:
                print("  → 使用公钥模式（新商户号）")
                init_params['public_key'] = settings.WECHAT_PLATFORM_CERT
                init_params['public_key_id'] = settings.WECHAT_PLATFORM_CERT_SERIAL_NO
                print(f"  → 公钥ID: {settings.WECHAT_PLATFORM_CERT_SERIAL_NO[:8]}...{settings.WECHAT_PLATFORM_CERT_SERIAL_NO[-8:]}")
            else:
                # 使用证书模式（需要自动下载或手动配置平台证书）
                print("  → 使用证书模式（将自动下载平台证书）")
                init_params['cert_dir'] = cert_dir

            self.wxpay = WeChatPay(**init_params)
            print("✅ 微信支付客户端初始化成功")

        except Exception as e:
            print(f"❌ 微信支付初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"微信支付配置错误: {str(e)}")

    def create_native_order(self, order):
        """
        创建 Native 支付订单 (扫码支付)
        返回支付二维码 URL
        """
        # 计算订单金额（单位：分）
        total_amount = int(order.total_amount * 100)

        # 计算订单过期时间
        time_expire = order.expires_at.strftime('%Y-%m-%dT%H:%M:%S+08:00') if order.expires_at else None

        # 构建订单数据
        out_trade_no = order.out_trade_no
        description = f'{order.product.name}'

        # 调用 Native 下单 API
        try:
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount={'total': total_amount},
                time_expire=time_expire,
            )

            print(f"微信支付 API 响应: code={code}, message type={type(message)}")

            if code == 200:
                # 检查 message 是否是字典
                if isinstance(message, dict):
                    code_url = message.get('code_url')
                    if code_url:
                        print(f"✅ 支付二维码生成成功: {code_url[:50]}...")
                        return code_url
                    else:
                        raise Exception(f'微信支付返回成功但缺少 code_url: {message}')
                else:
                    # message 是字符串或其他类型
                    raise Exception(f'微信支付返回格式错误: {type(message).__name__} - {message}')
            else:
                # 支付失败
                error_msg = message if isinstance(message, str) else str(message)
                raise Exception(f'微信支付下单失败 (code={code}): {error_msg}')
        except Exception as e:
            print(f"❌ 创建支付订单失败: {e}")
            raise

    def query_order(self, out_trade_no):
        """
        查询订单支付状态
        """
        code, message = self.wxpay.query(out_trade_no=out_trade_no)

        if code == 200:
            return message
        else:
            raise Exception(f'查询订单失败: {message}')

    def verify_notify(self, headers, body):
        """
        验证微信支付回调签名

        Args:
            headers: 请求头字典
            body: 请求体（bytes）

        Returns:
            验证成功返回解密后的数据，失败返回 None
        """
        try:
            result = self.wxpay.callback(headers, body)
            return result
        except Exception as e:
            print(f'回调验证失败: {e}')
            return None

    @staticmethod
    def generate_out_trade_no():
        """生成商户订单号"""
        timestamp = int(time.time())
        random_str = uuid.uuid4().hex[:8].upper()
        return f'ORDER_{timestamp}_{random_str}'
