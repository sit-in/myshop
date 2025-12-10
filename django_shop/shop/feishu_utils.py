"""飞书消息推送工具"""
import json
import requests
from django.conf import settings
from typing import Dict, List, Any


def send_feishu_message(webhook_url: str, msg_type: str, content: Dict[str, Any]) -> Dict:
    """发送飞书消息基础函数

    Args:
        webhook_url: 飞书 Webhook URL
        msg_type: 消息类型 (text, post, interactive)
        content: 消息内容

    Returns:
        响应结果字典
    """
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }

    payload = {
        'msg_type': msg_type,
    }

    if msg_type == 'interactive':
        payload['card'] = content
    else:
        payload['content'] = content

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"飞书消息发送失败: {e}")
        raise


def build_daily_report_card(stats_data: Dict[str, Any]) -> Dict[str, Any]:
    """构建每日销售报告消息卡片

    Args:
        stats_data: 统计数据字典，包含：
            - date: 日期
            - total_orders: 订单总数
            - total_revenue: 总收入
            - product_sales: 商品销售列表
            - low_stock_products: 低库存商品列表

    Returns:
        飞书消息卡片 JSON
    """
    # 构建标题（根据数据动态设置颜色）
    has_warning = len(stats_data.get('low_stock_products', [])) > 0
    title_color = 'red' if has_warning else 'blue'

    # 构建消息元素
    elements = []

    # 1. 基础统计信息
    elements.append({
        'tag': 'div',
        'text': {
            'tag': 'lark_md',
            'content': f"**📊 销售数据**\n"
                      f"- 订单总数：**{stats_data['total_orders']}** 笔\n"
                      f"- 总收入：**¥{stats_data['total_revenue']:.2f}**"
        }
    })

    # 2. 商品销售明细
    if stats_data.get('product_sales'):
        product_text = "**📦 商品销售详情**\n"
        for item in stats_data['product_sales']:
            product_text += f"- {item['product_name']}：{item['quantity']} 件 (¥{item['revenue']:.2f})\n"

        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': product_text
            }
        })

    # 3. 分割线
    elements.append({'tag': 'hr'})

    # 4. 库存预警
    if stats_data.get('low_stock_products'):
        warning_text = "**⚠️ 库存预警**\n"
        for item in stats_data['low_stock_products']:
            warning_text += f"- {item['product_name']}：仅剩 **{item['stock_count']}** 件\n"

        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': warning_text
            }
        })
    else:
        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': "✅ 所有商品库存充足"
            }
        })

    # 5. 操作按钮（可选）
    elements.append({
        'tag': 'action',
        'actions': [{
            'tag': 'button',
            'text': {
                'tag': 'plain_text',
                'content': '查看后台'
            },
            'url': f"{settings.SITE_URL}/admin/",
            'type': 'primary'
        }]
    })

    # 构建完整卡片
    card = {
        'header': {
            'title': {
                'tag': 'plain_text',
                'content': f"📈 {stats_data['date']} 销售日报"
            },
            'template': title_color
        },
        'elements': elements
    }

    return card


def send_daily_report(stats_data: Dict[str, Any]):
    """发送每日销售报告到飞书

    Args:
        stats_data: 统计数据
    """
    webhook_url = settings.FEISHU_WEBHOOK_URL
    card = build_daily_report_card(stats_data)
    return send_feishu_message(webhook_url, 'interactive', card)
