from decimal import Decimal

from django.db import models


class Product(models.Model):
    name = models.CharField('商品名称', max_length=200)
    slug = models.SlugField('URL别名', unique=True)
    description = models.TextField('商品描述', blank=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    display_order = models.IntegerField(
        '显示顺序',
        default=0,
        help_text='数字越小越靠前，相同数字按创建时间排序'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['display_order', '-created_at']

    def stock_count(self):
        """返回该商品的未售卡密数量"""
        return self.cards.filter(status='unsold').count()
    stock_count.short_description = '库存数量'

    def sold_count(self):
        """返回该商品已完成订单的购买总数量"""
        from django.db.models import Sum
        result = self.orders.filter(
            payment_status='paid',
            status='completed'
        ).aggregate(total_quantity=Sum('quantity'))
        return result['total_quantity'] or 0
    sold_count.short_description = '已售数量'

    def get_price_for_quantity(self, quantity):
        """根据购买数量获取对应的单价"""
        tier = self.price_tiers.filter(
            min_quantity__lte=quantity
        ).filter(
            models.Q(max_quantity__gte=quantity) | models.Q(max_quantity__isnull=True)
        ).first()

        if tier:
            return tier.unit_price

        # 降级方案：使用默认价格
        return self.price

    def calculate_total_price(self, quantity):
        """计算购买指定数量的总价"""
        unit_price = self.get_price_for_quantity(quantity)
        return unit_price * quantity

    def has_tiered_pricing(self):
        """检查是否配置了阶梯价格"""
        return self.price_tiers.exists()

    def get_price_tiers_display(self):
        """获取价格阶梯展示数据（用于模板）"""
        if not self.has_tiered_pricing():
            return None
        return self.price_tiers.all()

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
    unit_price_used = models.DecimalField(
        '成交单价',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='订单创建时使用的单价（根据阶梯价格计算）'
    )
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


class PriceTier(models.Model):
    """商品阶梯价格"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_tiers',
        verbose_name='商品'
    )
    min_quantity = models.PositiveIntegerField(
        '最小数量',
        help_text='此档位的最小购买数量（包含）'
    )
    max_quantity = models.PositiveIntegerField(
        '最大数量',
        null=True,
        blank=True,
        help_text='此档位的最大购买数量（包含），留空表示无上限'
    )
    unit_price = models.DecimalField(
        '单价',
        max_digits=10,
        decimal_places=2,
        help_text='此数量区间的单价'
    )
    display_order = models.IntegerField(
        '显示顺序',
        default=0
    )

    class Meta:
        verbose_name = '价格阶梯'
        verbose_name_plural = '价格阶梯'
        ordering = ['product', 'display_order', 'min_quantity']
        indexes = [
            models.Index(fields=['product', 'min_quantity', 'max_quantity']),
        ]

    def __str__(self):
        max_qty = f"{self.max_quantity}" if self.max_quantity else "∞"
        return f"{self.product.name} - {self.min_quantity}~{max_qty}个: ¥{self.unit_price}"

    def clean(self):
        """数据验证：确保数量和价格合理"""
        from django.core.exceptions import ValidationError

        if self.min_quantity < 1:
            raise ValidationError({'min_quantity': '最小数量必须大于等于1'})

        if self.max_quantity and self.max_quantity < self.min_quantity:
            raise ValidationError({'max_quantity': '最大数量必须大于等于最小数量'})

        if self.unit_price <= 0:
            raise ValidationError({'unit_price': '单价必须大于0'})


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
