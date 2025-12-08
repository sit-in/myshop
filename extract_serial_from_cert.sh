#!/bin/bash
# 从证书文件提取序列号的脚本

echo "====================================="
echo "从证书文件提取序列号"
echo "====================================="
echo ""
echo "使用方法："
echo "  bash extract_serial_from_cert.sh /path/to/apiclient_cert.pem"
echo ""

if [ -z "$1" ]; then
    echo "❌ 错误：请提供证书文件路径"
    echo "示例："
    echo "  bash extract_serial_from_cert.sh ~/Downloads/cert/apiclient_cert.pem"
    exit 1
fi

CERT_FILE="$1"

if [ ! -f "$CERT_FILE" ]; then
    echo "❌ 错误：文件不存在: $CERT_FILE"
    exit 1
fi

echo "证书文件: $CERT_FILE"
echo ""

# 提取序列号
echo "证书序列号："
SERIAL=$(openssl x509 -in "$CERT_FILE" -noout -serial | cut -d'=' -f2)
echo "  $SERIAL"
echo ""

# 提取有效期
echo "证书有效期："
openssl x509 -in "$CERT_FILE" -noout -dates
echo ""

# 提取主题信息
echo "证书主题："
openssl x509 -in "$CERT_FILE" -noout -subject
echo ""

echo "====================================="
echo "请将以下序列号配置到 Vercel:"
echo "  WECHAT_SERIAL_NO=$SERIAL"
echo "====================================="
