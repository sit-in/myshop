from datetime import timedelta
from io import BytesIO
import logging

import qrcode
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .email_utils import send_card_email
from .models import Card, Order, Product
from .wechat_pay import WeChatPayClient

logger = logging.getLogger(__name__)


def product_list(request):
    """Display all products."""
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})


def product_detail(request, slug):
    """商品详情页面"""
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {
        'product': product,
    })


@require_POST
def buy_product(request, slug):
    """创建订单并跳转支付页面"""
    product = get_object_or_404(Product, slug=slug)
    email = request.POST.get('email')
    quantity = int(request.POST.get('quantity', 1))

    if not email:
        return HttpResponseBadRequest("Email is required")

    # 验证购买数量
    if quantity < 1:
        return HttpResponseBadRequest("购买数量至少为 1")

    # 检查库存
    stock_count = product.cards.filter(status='unsold').count()
    if stock_count == 0:
        return render(request, 'shop/error.html', {
            'message': '抱歉，该商品已售罄。'
        }, status=400)

    if stock_count < quantity:
        return render(request, 'shop/error.html', {
            'message': f'抱歉，库存不足。当前库存仅剩 {stock_count} 件，您想购买 {quantity} 件。'
        }, status=400)

    # 创建订单（待支付状态）
    unit_price = product.get_price_for_quantity(quantity)
    order = Order.objects.create(
        email=email,
        product=product,  # 关联商品
        quantity=quantity,
        unit_price_used=unit_price,  # 新增：保存成交单价
        total_amount=unit_price * quantity,  # 修改：使用阶梯单价计算
        status='pending',
        payment_status='unpaid',
        out_trade_no=WeChatPayClient.generate_out_trade_no(),
        expires_at=timezone.now() + timedelta(minutes=settings.ORDER_EXPIRE_MINUTES),
    )

    # 检查是否启用测试模式
    test_mode = getattr(settings, 'PAYMENT_TEST_MODE', False)

    if test_mode:
        # 测试模式：直接模拟支付成功
        with transaction.atomic():
            # 批量分配卡密
            cards = (
                Card.objects
                .select_for_update(skip_locked=True)
                .filter(product=product, status='unsold')
                [:quantity]
            )
            cards_list = list(cards)

            if len(cards_list) == quantity:
                # 更新订单状态
                order.payment_status = 'paid'
                order.status = 'completed'
                order.transaction_id = f'TEST_{order.out_trade_no}'
                order.paid_at = timezone.now()
                order.qr_code_url = 'test://paid'
                order.save()

                # 批量更新卡密状态
                for card in cards_list:
                    card.status = 'sold'
                    card.order = order
                    card.save()

                # 发送邮件
                try:
                    send_card_email(order, cards_list)
                except Exception as e:
                    print(f"邮件发送失败: {e}")

                # 发送飞书通知
                try:
                    from .feishu_utils import send_order_notification
                    result = send_order_notification(order)
                    logger.info(f"[测试模式] 飞书通知发送成功: 订单#{order.id}, 响应={result}")
                except Exception as e:
                    logger.error(f"[测试模式] 飞书通知发送失败: 订单#{order.id}, 错误={e}", exc_info=True)
                    print(f"飞书通知发送失败: {e}")

                # 直接跳转到订单详情页
                return redirect('shop:order_detail', order_id=order.id)
            else:
                # 测试模式下也没有足够卡密，返回错误
                return render(request, 'shop/error.html', {
                    'message': f'抱歉，库存不足。当前仅剩 {len(cards_list)} 件。'
                }, status=400)

    # 生产模式：生成支付二维码
    try:
        # 初始化微信支付客户端（30秒超时）
        wechat_client = WeChatPayClient(timeout=30)

        # 创建支付订单（最多重试3次）
        qr_code_url = wechat_client.create_native_order(order, max_retries=3)

        order.qr_code_url = qr_code_url
        order.save()
    except Exception as e:
        logger.error(f"创建支付订单失败: {e}", exc_info=True)

        # 判断错误类型，提供不同的提示
        error_message = str(e)

        if 'timeout' in error_message.lower() or 'timed out' in error_message.lower():
            # 超时错误
            user_message = '支付系统连接超时，请稍后重试。如果问题持续出现，请联系客服。'
        elif '证书' in error_message or 'certificate' in error_message.lower():
            # 证书错误
            user_message = '支付配置错误，请联系客服处理。'
        else:
            # 其他错误
            user_message = f'支付系统错误：{error_message}'

        return render(request, 'shop/error.html', {
            'message': user_message,
            'detail': error_message if settings.DEBUG else None,  # 调试模式显示详细错误
        }, status=500)

    # 跳转到支付页面
    return redirect('shop:payment_page', order_id=order.id)


def payment_page(request, order_id):
    """显示支付二维码页面"""
    order = get_object_or_404(Order, id=order_id)

    # 检查订单状态
    if order.payment_status == 'paid':
        return redirect('shop:order_detail', order_id=order.id)

    if order.expires_at and order.expires_at < timezone.now():
        order.payment_status = 'expired'
        order.save()
        return render(request, 'shop/error.html', {
            'message': '订单已过期，请重新下单。'
        })

    return render(request, 'shop/payment.html', {
        'order': order,
    })


def generate_qr_code(request, order_id):
    """生成二维码图片"""
    order = get_object_or_404(Order, id=order_id)

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(order.qr_code_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')


@csrf_exempt
@require_POST
def wechat_payment_notify(request):
    """接收微信支付回调通知 (V3 API)"""
    try:
        # 获取请求头
        headers = {
            'Wechatpay-Signature': request.META.get('HTTP_WECHATPAY_SIGNATURE', ''),
            'Wechatpay-Timestamp': request.META.get('HTTP_WECHATPAY_TIMESTAMP', ''),
            'Wechatpay-Nonce': request.META.get('HTTP_WECHATPAY_NONCE', ''),
            'Wechatpay-Serial': request.META.get('HTTP_WECHATPAY_SERIAL', ''),
        }

        # 获取请求体
        body = request.body

        # 验证签名并解密
        wechat_client = WeChatPayClient()
        result = wechat_client.verify_notify(headers, body)

        if not result:
            return JsonResponse({'code': 'FAIL', 'message': '签名验证失败'})

        # 检查支付状态
        if result.get('event_type') != 'TRANSACTION.SUCCESS':
            return JsonResponse({'code': 'SUCCESS', 'message': '非成功通知'})

        # 获取订单信息
        resource = result.get('resource', {})
        out_trade_no = resource.get('out_trade_no')
        transaction_id = resource.get('transaction_id')
        trade_state = resource.get('trade_state')

        if trade_state != 'SUCCESS':
            return JsonResponse({'code': 'SUCCESS', 'message': '支付未成功'})

        # 查询订单
        with transaction.atomic():
            order = Order.objects.select_for_update().get(out_trade_no=out_trade_no)

            # 防止重复处理
            if order.payment_status == 'paid':
                return JsonResponse({'code': 'SUCCESS', 'message': '订单已处理'})

            # 批量分配卡密
            quantity = order.quantity
            cards = (
                Card.objects
                .select_for_update(skip_locked=True)
                .filter(product__id=order.product_id, status='unsold')
                [:quantity]
            )
            cards_list = list(cards)

            if len(cards_list) < quantity:
                # 库存不足，需要退款（这里简化处理）
                order.status = 'cancelled'
                order.save()
                return JsonResponse({'code': 'SUCCESS', 'message': f'库存不足，需要 {quantity} 件，仅剩 {len(cards_list)} 件'})

            # 更新订单状态
            order.payment_status = 'paid'
            order.status = 'completed'
            order.transaction_id = transaction_id
            order.paid_at = timezone.now()
            order.save()

            # 批量更新卡密状态
            for card in cards_list:
                card.status = 'sold'
                card.order = order
                card.save()

        # 发送邮件（异步执行更好）
        try:
            send_card_email(order, cards_list)
        except Exception as e:
            # 记录日志但不影响支付流程
            print(f"邮件发送失败: {e}")

        # 发送飞书通知
        try:
            from .feishu_utils import send_order_notification
            result = send_order_notification(order)
            logger.info(f"[微信回调] 飞书通知发送成功: 订单#{order.id}, 响应={result}")
        except Exception as e:
            # 记录日志但不影响支付流程
            logger.error(f"[微信回调] 飞书通知发送失败: 订单#{order.id}, 错误={e}", exc_info=True)
            print(f"飞书通知发送失败: {e}")

        return JsonResponse({'code': 'SUCCESS', 'message': '成功'})

    except Exception as e:
        print(f"支付回调处理失败: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'code': 'FAIL', 'message': str(e)})


def order_detail(request, order_id):
    """订单详情页面"""
    order = get_object_or_404(Order, id=order_id)
    cards = order.cards.all() if order.payment_status == 'paid' else []

    return render(request, 'shop/order_detail.html', {
        'order': order,
        'cards': cards,
    })


def check_payment_status(request, order_id):
    """AJAX 检查支付状态"""
    order = get_object_or_404(Order, id=order_id)

    # 如果订单还未支付，主动查询微信支付订单状态
    if order.payment_status == 'unpaid':
        try:
            wechat_client = WeChatPayClient()
            result = wechat_client.query_order(order.out_trade_no)

            print(f"查询订单状态: {result}")

            # 解析查询结果
            if isinstance(result, str):
                import json
                result = json.loads(result)

            trade_state = result.get('trade_state')

            # 如果支付成功，更新订单状态
            if trade_state == 'SUCCESS':
                with transaction.atomic():
                    # 重新获取订单（加锁）
                    order = Order.objects.select_for_update().get(id=order_id)

                    # 防止重复处理
                    if order.payment_status != 'paid':
                        # 批量分配卡密
                        quantity = order.quantity
                        cards = (
                            Card.objects
                            .select_for_update(skip_locked=True)
                            .filter(product=order.product, status='unsold')
                            [:quantity]
                        )
                        cards_list = list(cards)

                        if len(cards_list) == quantity:
                            # 更新订单
                            order.payment_status = 'paid'
                            order.status = 'completed'
                            order.transaction_id = result.get('transaction_id', '')
                            order.paid_at = timezone.now()
                            order.save()

                            # 批量更新卡密
                            for card in cards_list:
                                card.status = 'sold'
                                card.order = order
                                card.save()

                            print(f"✅ 订单 {order.id} 支付成功，已分配 {quantity} 个卡密")

                            # 发送邮件
                            try:
                                send_card_email(order, cards_list)
                            except Exception as e:
                                print(f"邮件发送失败: {e}")

                            # 发送飞书通知
                            try:
                                from .feishu_utils import send_order_notification
                                result = send_order_notification(order)
                                logger.info(f"[主动查询] 飞书通知发送成功: 订单#{order.id}, 响应={result}")
                            except Exception as e:
                                logger.error(f"[主动查询] 飞书通知发送失败: 订单#{order.id}, 错误={e}", exc_info=True)
                                print(f"飞书通知发送失败: {e}")

        except Exception as e:
            print(f"查询订单状态失败: {e}")
            import traceback
            traceback.print_exc()

    return JsonResponse({
        'payment_status': order.payment_status,
        'is_paid': order.payment_status == 'paid',
        'order_id': order.id,
    })
