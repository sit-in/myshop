"""微信支付工具类 - 使用微信支付 V3 API"""
import os
import time
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from wechatpayv3 import WeChatPay, WeChatPayType


class WeChatPayClient:
    """微信支付客户端 - 使用微信支付 V3 API"""

    def __init__(self, timeout=30):
        """初始化微信支付客户端

        Args:
            timeout: HTTP请求超时时间（秒），默认30秒
        """
        self.timeout = timeout

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
        print(f"  HTTP超时设置: {timeout} 秒")
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

            # 配置底层 requests Session 的超时和重试
            if hasattr(self.wxpay, '_core'):
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry

                # 创建重试策略
                retry_strategy = Retry(
                    total=3,  # 最多重试3次
                    backoff_factor=1,  # 指数退避因子
                    status_forcelist=[429, 500, 502, 503, 504],  # 对这些HTTP状态码重试
                    allowed_methods=["GET", "POST"]  # 允许重试的HTTP方法
                )

                adapter = HTTPAdapter(max_retries=retry_strategy)

                # 如果 _core 有 session 属性，配置它
                if hasattr(self.wxpay._core, 'session'):
                    self.wxpay._core.session.mount("https://", adapter)
                    self.wxpay._core.session.mount("http://", adapter)
                    print(f"✅ 已配置 HTTP 重试策略: 最多3次, 超时{timeout}秒")

            print("✅ 微信支付客户端初始化成功")

        except Exception as e:
            print(f"❌ 微信支付初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"微信支付配置错误: {str(e)}")

    def create_native_order(self, order, max_retries=3):
        """
        创建 Native 支付订单 (扫码支付)
        返回支付二维码 URL

        Args:
            order: Order 对象
            max_retries: 最大重试次数，默认3次

        Returns:
            code_url: 支付二维码链接
        """
        # 计算订单金额（单位：分）
        total_amount = int(order.total_amount * 100)

        # 计算订单过期时间
        time_expire = order.expires_at.strftime('%Y-%m-%dT%H:%M:%S+08:00') if order.expires_at else None

        # 构建订单数据
        out_trade_no = order.out_trade_no
        description = f'{order.product.name}'

        # 重试逻辑
        last_exception = None
        for attempt in range(max_retries):
            try:
                print(f"\n{'='*60}")
                print(f"尝试创建支付订单 (第 {attempt + 1}/{max_retries} 次)")
                print(f"  订单号: {out_trade_no}")
                print(f"  金额: {total_amount / 100:.2f} 元")
                print(f"  商品: {description}")
                print(f"{'='*60}\n")

                # 调用 Native 下单 API
                code, message = self.wxpay.pay(
                    description=description,
                    out_trade_no=out_trade_no,
                    amount={'total': total_amount},
                    time_expire=time_expire,
                )

                print(f"微信支付 API 响应: code={code}, message type={type(message)}")

                if code == 200:
                    # 检查 message 类型并解析
                    if isinstance(message, str):
                        # 公钥模式返回 JSON 字符串，需要解析
                        try:
                            import json
                            message_dict = json.loads(message)
                            print(f"✅ JSON 解析成功: {message_dict}")
                        except json.JSONDecodeError as je:
                            raise Exception(f'JSON 解析失败: {message}')
                    elif isinstance(message, dict):
                        # 证书模式直接返回字典
                        message_dict = message
                    else:
                        raise Exception(f'未知的响应类型: {type(message).__name__}')

                    # 提取 code_url
                    code_url = message_dict.get('code_url')
                    if code_url:
                        print(f"✅ 支付二维码生成成功: {code_url}")
                        return code_url
                    else:
                        raise Exception(f'微信支付返回成功但缺少 code_url: {message_dict}')
                else:
                    # 支付失败
                    error_msg = message if isinstance(message, str) else str(message)
                    raise Exception(f'微信支付下单失败 (code={code}): {error_msg}')

            except Exception as e:
                last_exception = e
                error_str = str(e)

                # 判断是否是网络超时错误
                is_timeout = (
                    'timeout' in error_str.lower() or
                    'timed out' in error_str.lower() or
                    'connection' in error_str.lower()
                )

                print(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
                print(f"   错误类型: {'网络超时' if is_timeout else '其他错误'}")

                if attempt < max_retries - 1:
                    # 还有重试机会，计算等待时间（指数退避）
                    wait_time = 2 ** attempt  # 1秒、2秒、4秒
                    print(f"   ⏳ 等待 {wait_time} 秒后重试...\n")
                    time.sleep(wait_time)
                else:
                    # 所有重试都失败
                    print(f"\n{'='*60}")
                    print(f"❌ 创建支付订单失败，已尝试 {max_retries} 次")
                    print(f"最后错误: {last_exception}")
                    print(f"{'='*60}\n")

                    # 根据错误类型返回更友好的提示
                    if is_timeout:
                        raise Exception(f'微信支付服务连接超时，请稍后重试。已尝试{max_retries}次。详细错误: {last_exception}')
                    else:
                        raise Exception(f'微信支付下单失败: {last_exception}')

        # 理论上不会到这里，但为了安全
        if last_exception:
            raise last_exception

    def query_order(self, out_trade_no, max_retries=3):
        """
        查询订单支付状态

        Args:
            out_trade_no: 商户订单号
            max_retries: 最大重试次数，默认3次

        Returns:
            订单详情字典
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                print(f"尝试查询订单状态 (第 {attempt + 1}/{max_retries} 次): {out_trade_no}")

                code, message = self.wxpay.query(out_trade_no=out_trade_no)

                print(f"查询订单 API 响应: code={code}, message type={type(message)}")

                if code == 200:
                    # 检查 message 类型并解析（与创建订单逻辑一致）
                    if isinstance(message, str):
                        # 公钥模式返回 JSON 字符串
                        try:
                            import json
                            message_dict = json.loads(message)
                            print(f"✅ 查询结果解析成功")
                            return message_dict
                        except json.JSONDecodeError:
                            raise Exception(f'JSON 解析失败: {message}')
                    elif isinstance(message, dict):
                        # 证书模式直接返回字典
                        return message
                    else:
                        raise Exception(f'未知的响应类型: {type(message).__name__}')
                else:
                    error_msg = message if isinstance(message, str) else str(message)
                    raise Exception(f'查询订单失败 (code={code}): {error_msg}')

            except Exception as e:
                last_exception = e
                print(f"❌ 第 {attempt + 1} 次查询失败: {e}")

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 查询订单失败，已尝试 {max_retries} 次: {e}")
                    raise

        if last_exception:
            raise last_exception

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
