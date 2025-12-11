"""邮件发送工具"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_card_email(order, cards):
    """发送卡密到用户邮箱

    Args:
        order: 订单对象
        cards: 卡密对象列表或单个卡密对象
    """
    # 兼容单个卡密和多个卡密
    if not isinstance(cards, list):
        cards = [cards]

    subject = f'【数字商店】您的订单 #{order.id} 已完成'

    html_message = render_to_string('shop/email/card_delivery.html', {
        'order': order,
        'cards': cards,
    })

    # 构建纯文本邮件内容
    cards_content = '\n'.join([f'{i+1}. {card.content}' for i, card in enumerate(cards)])

    plain_message = f"""
尊敬的用户，您好！

您的订单 #{order.id} 已支付成功。

商品名称：{cards[0].product.name}
购买数量：{len(cards)} 件
订单金额：¥{order.total_amount}

商品使用说明：
{cards[0].product.description}

您的卡密信息：
{cards_content}

请妥善保管您的卡密信息！

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
