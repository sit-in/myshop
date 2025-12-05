"""微信支付工具类"""
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from wechatpy.pay import WeChatPay


class WeChatPayClient:
    """微信支付客户端"""

    def __init__(self):
        self.client = WeChatPay(
            appid=settings.WECHAT_PAY_APP_ID,
            api_key=settings.WECHAT_PAY_API_KEY,
            mch_id=settings.WECHAT_PAY_MCH_ID,
            mch_cert=settings.WECHAT_PAY_MCH_CERT,
            mch_key=settings.WECHAT_PAY_MCH_KEY,
        )

    def create_native_order(self, order):
        """创建 Native 支付订单"""
        result = self.client.order.create(
            trade_type='NATIVE',
            body=f'{order.product.name}',
            out_trade_no=order.out_trade_no,
            total_fee=int(order.total_amount * 100),  # 转换为分
            notify_url=settings.WECHAT_PAY_NOTIFY_URL,
            product_id=str(order.id),
        )
        return result.get('code_url')

    def query_order(self, out_trade_no):
        """查询订单支付状态"""
        return self.client.order.query(out_trade_no=out_trade_no)

    def verify_notify(self, data):
        """验证微信支付回调签名"""
        return self.client.parse_payment_result(data)

    @staticmethod
    def generate_out_trade_no():
        """生成商户订单号"""
        timestamp = int(time.time())
        random_str = uuid.uuid4().hex[:8].upper()
        return f'ORDER_{timestamp}_{random_str}'
