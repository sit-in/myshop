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

        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=settings.WECHAT_MCH_ID,
            private_key=settings.WECHAT_PRIVATE_KEY,
            cert_serial_no=settings.WECHAT_SERIAL_NO,
            apiv3_key=settings.WECHAT_API_V3_KEY,
            appid=settings.WECHAT_APP_ID,
            notify_url=settings.WECHAT_PAY_NOTIFY_URL,
            cert_dir=cert_dir,  # 证书缓存目录
        )

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
        code, message = self.wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={'total': total_amount},
            time_expire=time_expire,
        )

        if code == 200:
            # 返回二维码链接
            return message.get('code_url')
        else:
            raise Exception(f'微信支付下单失败: {message}')

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
