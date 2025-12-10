"""销售统计数据服务"""
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.conf import settings
from typing import Dict, List, Any

from .models import Order, Product


def get_today_stats(target_date=None) -> Dict[str, Any]:
    """获取指定日期的销售统计数据

    Args:
        target_date: 目标日期（默认为今天）

    Returns:
        统计数据字典
    """
    # 确定统计日期范围（当天 00:00:00 到 23:59:59）
    if target_date is None:
        target_date = timezone.now().date()

    start_time = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
    end_time = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))

    # 查询今日已完成订单
    today_orders = Order.objects.filter(
        payment_status='paid',
        status='completed',
        paid_at__gte=start_time,
        paid_at__lte=end_time
    )

    # 1. 基础统计
    total_orders = today_orders.count()
    total_revenue = today_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    # 2. 各商品销售统计
    product_sales = (
        today_orders
        .values('product__name', 'product_id')
        .annotate(
            quantity=Sum('quantity'),
            revenue=Sum('total_amount')
        )
        .order_by('-revenue')
    )

    # 格式化商品销售数据
    product_sales_list = [
        {
            'product_name': item['product__name'],
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'revenue': float(item['revenue'])
        }
        for item in product_sales
    ]

    # 3. 库存预警检查
    stock_threshold = getattr(settings, 'STOCK_WARNING_THRESHOLD', 10)
    low_stock_products = get_low_stock_products(stock_threshold)

    return {
        'date': target_date.strftime('%Y-%m-%d'),
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'product_sales': product_sales_list,
        'low_stock_products': low_stock_products,
    }


def get_low_stock_products(threshold: int) -> List[Dict[str, Any]]:
    """获取库存低于阈值的商品列表

    Args:
        threshold: 库存阈值

    Returns:
        低库存商品列表
    """
    products = Product.objects.all()
    low_stock = []

    for product in products:
        stock_count = product.stock_count()
        if stock_count < threshold:
            low_stock.append({
                'product_id': product.id,
                'product_name': product.name,
                'stock_count': stock_count,
                'threshold': threshold
            })

    return low_stock


def get_weekly_stats() -> Dict[str, Any]:
    """获取本周统计数据（可选扩展功能）

    预留接口，用于未来扩展周报功能
    """
    pass
