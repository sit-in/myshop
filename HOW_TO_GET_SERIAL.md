# 如何获取正确的微信支付证书序列号

## 问题描述
微信支付初始化失败，错误：`No wechatpay platform certificate`
原因：证书序列号与私钥不匹配

## 解决方案

### 方法1：从其他正常运行的平台复制（最快）⭐

1. 登录您其他正常使用微信支付的平台
2. 查看环境变量配置
3. 找到 `WECHAT_SERIAL_NO` 的值
4. 复制到 Vercel 中

### 方法2：从微信商户平台查看

1. 登录微信商户平台
   ```
   https://pay.weixin.qq.com
   ```

2. 导航路径：
   ```
   账户中心 → API安全 → API证书
   ```

3. 查看证书列表
   - 会显示所有有效证书
   - 每个证书都有对应的序列号
   - 找到当前使用的证书序列号

4. 注意事项：
   - 如果有多个证书，选择最新的或正在使用的
   - 序列号是40位十六进制字符
   - 示例：`5E3C7C1A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E`

### 方法3：从证书文件提取

如果您有 `apiclient_cert.pem` 文件：

```bash
# 方法1：使用 openssl 命令
openssl x509 -in apiclient_cert.pem -noout -serial

# 方法2：使用提供的脚本
bash extract_serial_from_cert.sh /path/to/apiclient_cert.pem
```

### 方法4：从私钥文件反推（不可行）

❌ 注意：无法从私钥文件直接获取证书序列号
✅ 必须从证书文件或商户平台获取

## 更新 Vercel 配置

获取正确的序列号后：

1. 访问 Vercel Dashboard
   ```
   https://vercel.com/你的项目/settings/environment-variables
   ```

2. 编辑 `WECHAT_SERIAL_NO`
3. 粘贴正确的序列号（40位）
4. 保存并重新部署

## 验证配置

部署完成后，查看 Vercel 日志，应该看到：

```
============================================================
微信支付初始化配置检查:
  商户号 (mchid): 1586320901
  AppID: wx2f5f0f2135ea10d4
  证书序列号: 正确的序列号...
  APIv3密钥长度: 32 字符
  私钥格式: 包含 BEGIN PRIVATE KEY
  证书目录: /tmp/wechatpay_certs
============================================================
✅ 微信支付客户端初始化成功
```

## 常见问题

### Q1: 如何知道使用哪个证书？
A: 如果有多个证书，使用与其他正常运行平台相同的证书序列号。

### Q2: 证书会过期吗？
A: 会。API证书有效期通常是5年，过期前需要更新。

### Q3: 更新证书序列号会影响其他平台吗？
A: 不会。证书序列号只是标识符，不影响其他配置。

### Q4: 如果仍然失败怎么办？
A: 确保以下配置与其他正常运行平台完全一致：
- WECHAT_API_V3_KEY（已确认正确）
- WECHAT_SERIAL_NO
- WECHAT_PRIVATE_KEY
- WECHAT_MCH_ID
- WECHAT_APP_ID

## 联系支持

如果以上方法都无法解决，可能需要：
1. 重新申请API证书
2. 联系微信支付技术支持
3. 检查商户号是否已开通Native支付权限
