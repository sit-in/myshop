from datetime import datetime, timedelta
from io import BytesIO

import qrcode
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .email_utils import send_card_email
from .models import Card, Order, Product
from .wechat_pay import WeChatPayClient


def product_list(request):
    """Display all products."""
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})


@require_POST
def buy_product(request, slug):
    """创建订单并跳转支付页面"""
    product = get_object_or_404(Product, slug=slug)
    email = request.POST.get('email')

    if not email:
        return HttpResponseBadRequest("Email is required")

    # 检查库存
    stock_count = product.cards.filter(status='unsold').count()
    if stock_count == 0:
        return render(request, 'shop/error.html', {
            'message': '抱歉，该商品已售罄。'
        }, status=400)

    # 创建订单（待支付状态）
    order = Order.objects.create(
        email=email,
        product=product,  # 关联商品
        total_amount=product.price,
        status='pending',
        payment_status='unpaid',
        out_trade_no=WeChatPayClient.generate_out_trade_no(),
        expires_at=datetime.now() + timedelta(minutes=settings.ORDER_EXPIRE_MINUTES),
    )

    # 检查是否启用测试模式
    test_mode = getattr(settings, 'PAYMENT_TEST_MODE', False)

    if test_mode:
        # 测试模式：直接模拟支付成功
        with transaction.atomic():
            # 分配卡密
            card = (
                Card.objects
                .select_for_update(skip_locked=True)
                .filter(product=product, status='unsold')
                .first()
            )

            if card:
                # 更新订单状态
                order.payment_status = 'paid'
                order.status = 'completed'
                order.transaction_id = f'TEST_{order.out_trade_no}'
                order.paid_at = datetime.now()
                order.qr_code_url = 'test://paid'
                order.save()

                # 更新卡密状态
                card.status = 'sold'
                card.order = order
                card.save()

                # 直接跳转到订单详情页
                return redirect('shop:order_detail', order_id=order.id)

    # 生产模式：生成支付二维码
    try:
        wechat_client = WeChatPayClient()
        qr_code_url = wechat_client.create_native_order(order)
        order.qr_code_url = qr_code_url
        order.save()
    except Exception as e:
        return render(request, 'shop/error.html', {
            'message': f'支付系统错误：{str(e)}'
        }, status=500)

    # 跳转到支付页面
    return redirect('shop:payment_page', order_id=order.id)


def payment_page(request, order_id):
    """显示支付二维码页面"""
    order = get_object_or_404(Order, id=order_id)

    # 检查订单状态
    if order.payment_status == 'paid':
        return redirect('shop:order_detail', order_id=order.id)

    if order.expires_at and order.expires_at < datetime.now():
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
    """接收微信支付回调通知"""
    try:
        # 解析 XML 数据
        data = request.body
        wechat_client = WeChatPayClient()

        # 验证签名
        result = wechat_client.verify_notify(data)

        if result.get('return_code') != 'SUCCESS' or result.get('result_code') != 'SUCCESS':
            return HttpResponse('FAIL', content_type='text/plain')

        # 获取订单号
        out_trade_no = result.get('out_trade_no')
        transaction_id = result.get('transaction_id')

        # 查询订单
        with transaction.atomic():
            order = Order.objects.select_for_update().get(out_trade_no=out_trade_no)

            # 防止重复处理
            if order.payment_status == 'paid':
                return HttpResponse('SUCCESS', content_type='text/plain')

            # 分配卡密
            card = (
                Card.objects
                .select_for_update(skip_locked=True)
                .filter(product__id=order.product_id, status='unsold')
                .first()
            )

            if not card:
                # 库存不足，需要退款（这里简化处理）
                order.status = 'cancelled'
                order.save()
                return HttpResponse('SUCCESS', content_type='text/plain')

            # 更新订单状态
            order.payment_status = 'paid'
            order.status = 'completed'
            order.transaction_id = transaction_id
            order.paid_at = datetime.now()
            order.save()

            # 更新卡密状态
            card.status = 'sold'
            card.order = order
            card.save()

        # 发送邮件（异步执行更好）
        try:
            send_card_email(order, card)
        except Exception as e:
            # 记录日志但不影响支付流程
            print(f"邮件发送失败: {e}")

        return HttpResponse('SUCCESS', content_type='text/plain')

    except Exception as e:
        print(f"支付回调处理失败: {e}")
        return HttpResponse('FAIL', content_type='text/plain')


def order_detail(request, order_id):
    """订单详情页面"""
    order = get_object_or_404(Order, id=order_id)
    card = order.cards.first() if order.payment_status == 'paid' else None

    return render(request, 'shop/order_detail.html', {
        'order': order,
        'card': card,
    })


def check_payment_status(request, order_id):
    """AJAX 检查支付状态"""
    order = get_object_or_404(Order, id=order_id)

    return JsonResponse({
        'payment_status': order.payment_status,
        'is_paid': order.payment_status == 'paid',
        'order_id': order.id,
    })
