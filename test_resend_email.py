#!/usr/bin/env python
"""测试 Resend 邮件发送功能"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django_shop'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def test_simple_email():
    """测试简单文本邮件"""
    print("正在测试简单文本邮件...")
    print(f"发件人: {settings.DEFAULT_FROM_EMAIL}")
    print(f"SMTP 服务器: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")

    try:
        send_mail(
            subject='Resend 邮件测试',
            message='这是一封来自 Resend 的测试邮件。\n\n如果您收到这封邮件，说明邮件配置成功！',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['zimawangluo@myshop.fyyd.net'],
            fail_silently=False,
        )
        print("✓ 简单文本邮件发送成功！")
        return True
    except Exception as e:
        print(f"✗ 邮件发送失败: {e}")
        return False

def test_html_email():
    """测试 HTML 邮件"""
    print("\n正在测试 HTML 邮件...")

    try:
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #4CAF50;">Resend 邮件测试</h2>
            <p>这是一封来自 <strong>Resend</strong> 的 HTML 测试邮件。</p>
            <p>如果您看到这封格式化的邮件，说明 HTML 邮件配置成功！</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                发送时间: 测试邮件<br>
                发件人: MyShop 商城系统
            </p>
        </body>
        </html>
        """

        email = EmailMessage(
            subject='Resend HTML 邮件测试',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['zimawangluo@myshop.fyyd.net'],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

        print("✓ HTML 邮件发送成功！")
        return True
    except Exception as e:
        print(f"✗ HTML 邮件发送失败: {e}")
        return False

def test_order_notification():
    """测试订单通知邮件（模拟实际使用场景）"""
    print("\n正在测试订单通知邮件...")

    try:
        order_number = "TEST202512080001"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #4CAF50; color: white; padding: 20px; text-align: center;">
                <h1>订单确认</h1>
            </div>
            <div style="padding: 20px;">
                <p>您好，</p>
                <p>感谢您的购买！您的订单已成功创建。</p>

                <div style="background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0;">订单信息</h3>
                    <p><strong>订单号:</strong> {order_number}</p>
                    <p><strong>订单状态:</strong> 待支付</p>
                    <p><strong>订单金额:</strong> ¥99.00</p>
                </div>

                <p>请尽快完成支付，订单将在 30 分钟后自动取消。</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://myshop.fyyd.net"
                       style="background: #4CAF50; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        查看订单详情
                    </a>
                </div>
            </div>
            <div style="background: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px;">
                <p>此邮件由 MyShop 商城系统自动发送，请勿回复。</p>
                <p>© 2025 MyShop. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        email = EmailMessage(
            subject=f'订单确认 - {order_number}',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['zimawangluo@myshop.fyyd.net'],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

        print("✓ 订单通知邮件发送成功！")
        return True
    except Exception as e:
        print(f"✗ 订单通知邮件发送失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Resend 邮件服务测试")
    print("=" * 50)

    # 显示当前配置
    print(f"\n当前邮件配置:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()

    # 运行测试
    results = []
    results.append(test_simple_email())
    results.append(test_html_email())
    results.append(test_order_notification())

    # 总结
    print("\n" + "=" * 50)
    print(f"测试完成: {sum(results)}/3 通过")
    print("=" * 50)

    if all(results):
        print("\n✓ 所有测试通过！Resend 邮件服务配置成功。")
        print("\n请检查您的邮箱，确认收到了 3 封测试邮件：")
        print("  1. 简单文本邮件")
        print("  2. HTML 格式邮件")
        print("  3. 订单通知邮件（模拟真实场景）")
    else:
        print("\n✗ 部分测试失败，请检查配置和错误信息。")
