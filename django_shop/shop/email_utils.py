"""邮件发送工具"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_card_email(order, card):
    """发送卡密到用户邮箱"""
    subject = f'【数字商店】您的订单 #{order.id} 已完成'

    html_message = render_to_string('shop/email/card_delivery.html', {
        'order': order,
        'card': card,
    })

    plain_message = f"""
尊敬的用户，您好！

您的订单 #{order.id} 已支付成功。

商品名称：{card.product.name}
订单金额：¥{order.total_amount}
卡密内容：{card.content}

感谢您的购买！

---
数字商店
    """

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )
