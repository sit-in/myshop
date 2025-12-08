from decimal import Decimal

from django.db import models


class Product(models.Model):
    name = models.CharField('商品名称', max_length=200)
    slug = models.SlugField('URL别名', unique=True)
    description = models.TextField('商品描述', blank=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']

    def stock_count(self):
        """返回该商品的未售卡密数量"""
        return self.cards.filter(status='unsold').count()
    stock_count.short_description = '库存数量'

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('refunded', '已退款'),
        ('expired', '已过期'),
    ]

    # 商品关联
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders', verbose_name='商品', null=True, blank=True)

    email = models.EmailField('买家邮箱')
    quantity = models.PositiveIntegerField('购买数量', default=1)
    total_amount = models.DecimalField('订单金额', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField('订单状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('下单时间', auto_now_add=True)

    # 支付相关字段
    payment_status = models.CharField('支付状态', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    out_trade_no = models.CharField('商户订单号', max_length=64, unique=True, db_index=True, blank=True)
    transaction_id = models.CharField('微信支付交易号', max_length=64, blank=True, null=True)
    qr_code_url = models.URLField('支付二维码链接', blank=True, null=True, max_length=500)
    paid_at = models.DateTimeField('支付时间', blank=True, null=True)
    expires_at = models.DateTimeField('订单过期时间', blank=True, null=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"订单 #{self.pk} - {self.email}"


class Card(models.Model):
    STATUS_CHOICES = [
        ('unsold', '未售出'),
        ('sold', '已售出'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cards', verbose_name='所属商品')
    content = models.TextField('卡密内容', help_text='数字内容（如：激活码、下载链接等）')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='unsold')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards', verbose_name='关联订单')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '卡密'
        verbose_name_plural = '卡密'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.get_status_display()}"
