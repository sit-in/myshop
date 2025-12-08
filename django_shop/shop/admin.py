from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from openpyxl import load_workbook
from django.contrib import messages

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


class ExcelImportForm(forms.Form):
    """Excel 导入表单"""
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label='选择商品',
        help_text='选择要导入卡密的商品'
    )
    excel_file = forms.FileField(
        label='Excel 文件',
        help_text='上传包含卡密的 Excel 文件（仅支持 .xlsx 格式）。第一列为卡密内容，从第二行开始读取。'
    )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'status', 'short_content', 'order', 'created_at')
    list_filter = ('status', 'product')
    search_fields = ('content',)
    raw_id_fields = ('order',)
    list_editable = ('status',)
    ordering = ['-created_at']

    @admin.display(description='卡密内容')
    def short_content(self, obj):
        if len(obj.content) > 30:
            return obj.content[:30] + '...'
        return obj.content

    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='card_import_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        """处理 Excel 导入"""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.cleaned_data['product']
                excel_file = request.FILES['excel_file']

                # 验证文件格式
                if not excel_file.name.endswith('.xlsx'):
                    messages.error(request, '只支持 .xlsx 格式的 Excel 文件')
                    return redirect('.')

                try:
                    # 加载 Excel 文件
                    workbook = load_workbook(excel_file, read_only=True)
                    sheet = workbook.active

                    # 读取卡密（从第二行开始，第一列）
                    cards_to_create = []
                    for row in sheet.iter_rows(min_row=2, max_col=1, values_only=True):
                        card_content = row[0]
                        if card_content:  # 跳过空行
                            card_content = str(card_content).strip()
                            if card_content:
                                cards_to_create.append(Card(
                                    product=product,
                                    content=card_content,
                                    status='unsold'
                                ))

                    # 批量创建卡密
                    if cards_to_create:
                        Card.objects.bulk_create(cards_to_create)
                        messages.success(request, f'成功导入 {len(cards_to_create)} 个卡密到商品「{product.name}」')
                    else:
                        messages.warning(request, '未找到有效的卡密数据')

                    return redirect('..')

                except Exception as e:
                    messages.error(request, f'导入失败：{str(e)}')
                    return redirect('.')
        else:
            form = ExcelImportForm()

        context = {
            'form': form,
            'title': 'Excel 批量导入卡密',
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
            'has_permission': True,
        }
        return render(request, 'admin/card_import_excel.html', context)

    # 在列表页添加导入按钮
    change_list_template = 'admin/card_change_list.html'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'quantity', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    list_editable = ('status',)
    ordering = ['-created_at']
