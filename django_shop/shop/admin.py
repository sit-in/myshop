from django.contrib import admin

from .models import Card, Order, Product

# 自定义 Admin 站点标题
admin.site.site_header = '数字商店管理后台'
admin.site.site_title = '数字商店'
admin.site.index_title = '后台管理'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_count', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ['-created_at']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'status', 'short_content', 'order', 'created_at')
    list_filter = ('status', 'product')
    search_fields = ('content',)
    # raw_id_fields = ('product', 'order')  # 移除此行，改用普通下拉选择
    raw_id_fields = ('order',)  # 只对 order 使用搜索框
    list_editable = ('status',)
    ordering = ['-created_at']

    @admin.display(description='卡密内容')
    def short_content(self, obj):
        if len(obj.content) > 30:
            return obj.content[:30] + '...'
        return obj.content


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    list_editable = ('status',)
    ordering = ['-created_at']
