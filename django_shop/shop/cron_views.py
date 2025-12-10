"""定时任务视图（用于 Vercel Cron Jobs）"""
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .stats_service import get_today_stats
from .feishu_utils import send_daily_report


@csrf_exempt
@require_GET
def daily_report_cron(request):
    """每日销售报告定时任务

    安全策略：
    1. 仅接受 GET 请求
    2. 验证 User-Agent 为 vercel-cron/1.0
    3. 可选：验证自定义密钥（环境变量）
    """
    # 安全验证：检查 User-Agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent.startswith('vercel-cron/'):
        return HttpResponseForbidden('Forbidden: Invalid User-Agent')

    # 可选：额外密钥验证（更安全）
    secret_key = request.GET.get('secret')
    expected_secret = getattr(settings, 'CRON_SECRET_KEY', None)
    if expected_secret and secret_key != expected_secret:
        return HttpResponseForbidden('Forbidden: Invalid secret key')

    try:
        # 1. 获取统计数据
        stats_data = get_today_stats()

        # 2. 发送飞书通知
        result = send_daily_report(stats_data)

        return JsonResponse({
            'success': True,
            'message': 'Daily report sent successfully',
            'stats': stats_data,
            'feishu_response': result
        })

    except Exception as e:
        print(f"定时任务执行失败: {e}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_GET
def test_feishu_notification(request):
    """测试飞书通知（手动触发）

    使用方式：访问 /api/cron/test-feishu/?secret=YOUR_SECRET
    """
    # 简单的密钥保护
    secret_key = request.GET.get('secret')
    expected_secret = getattr(settings, 'CRON_SECRET_KEY', None)
    if expected_secret and secret_key != expected_secret:
        return HttpResponseForbidden('Forbidden: Invalid secret key')

    try:
        # 构建测试数据
        test_stats = {
            'date': '2025-12-10',
            'total_orders': 5,
            'total_revenue': 500.00,
            'product_sales': [
                {'product_name': '测试商品A', 'quantity': 3, 'revenue': 300.00},
                {'product_name': '测试商品B', 'quantity': 2, 'revenue': 200.00},
            ],
            'low_stock_products': [
                {'product_name': '测试商品C', 'stock_count': 5, 'threshold': 10}
            ]
        }

        result = send_daily_report(test_stats)

        return JsonResponse({
            'success': True,
            'message': 'Test notification sent',
            'result': result
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
