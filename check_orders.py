#!/usr/bin/env python3
"""快速检查订单状态的脚本"""

import os
import sys
import django

# 添加 Django 项目路径
sys.path.insert(0, '/Users/xiaoxiao/Desktop/AI_coding/myshop_git/myshop/django_shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.models import Order

print("=" * 60)
print("最近 5 个订单状态")
print("=" * 60)

orders = Order.objects.all().order_by('-created_at')[:5]

if not orders:
    print("暂无订单")
else:
    for order in orders:
        print(f"\n订单 #{order.id}")
        print(f"  商品: {order.product.name if order.product else 'N/A'}")
        print(f"  金额: ¥{order.total_amount}")
        print(f"  邮箱: {order.email}")
        print(f"  订单号: {order.out_trade_no}")
        print(f"  支付状态: {order.get_payment_status_display()}")
        print(f"  订单状态: {order.get_status_display()}")
        print(f"  创建时间: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if order.paid_at:
            print(f"  支付时间: {order.paid_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if order.transaction_id:
            print(f"  微信交易号: {order.transaction_id}")

        # 检查卡密
        cards = order.cards.all()
        if cards:
            print(f"  已分配卡密: {cards.count()} 张")
            for card in cards:
                print(f"    - {card.content[:20]}...")

        print("-" * 60)

print("\n库存情况:")
from shop.models import Product, Card
for product in Product.objects.all():
    stock = product.cards.filter(status='unsold').count()
    total = product.cards.count()
    print(f"  {product.name}: {stock}/{total} 张可用")
