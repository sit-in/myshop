from django.urls import path

from . import views
from . import cron_views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('buy/<slug:slug>/', views.buy_product, name='buy_product'),

    # 支付相关
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('payment/qrcode/<int:order_id>/', views.generate_qr_code, name='qr_code'),
    path('payment/notify/', views.wechat_payment_notify, name='payment_notify'),
    path('payment/status/<int:order_id>/', views.check_payment_status, name='payment_status'),

    # 订单查询
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # 定时任务
    path('api/cron/daily-report/', cron_views.daily_report_cron, name='daily_report_cron'),
    path('api/cron/test-feishu/', cron_views.test_feishu_notification, name='test_feishu'),
]
