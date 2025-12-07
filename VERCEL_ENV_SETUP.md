# Vercel 环境变量配置指南

## ⚠️ 重要：必须配置的环境变量

在 Vercel 项目中进入 **Settings** → **Environment Variables**，添加以下所有变量：

---

## 🔴 必需配置（缺少会导致部署失败）

### 1. 数据库连接
```bash
DATABASE_URL=postgresql://postgres:uku!xpt@EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres
```

**重要提示**：
- 在 Vercel 环境变量中，密码的特殊字符（`!` 和 `@`）**不需要**进行 URL 编码
- 直接使用原始密码：`uku!xpt@EBY1wzb-mwu`
- **不要**使用：`uku%21xpt%40EBY1wzb-mwu`（这是错误的）

### 2. Django 密钥
```bash
SECRET_KEY=生成一个随机的强密钥（50+ 字符）
DEBUG=False
```

生成新密钥的命令：
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🟡 微信公众号配置

```bash
WECHAT_APP_ID=wx2f5f0f2135ea10d4
WECHAT_APP_SECRET=88c62413dcdb58ee63348b2ba2465246
```

---

## 🟡 微信支付配置

```bash
WECHAT_MCH_ID=1586320901
WECHAT_API_V3_KEY=xgWzZEMZbzrW0syJLghqLuvZCR1ej3kQ
WECHAT_SERIAL_NO=78CE472193EC6C6B270550B62882FB87D9F0E980
```

### 微信支付私钥（重要！）

```bash
WECHAT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDE6nMJh53EnEcJ
A/Ulr2kDtN/xf0BIU26lFhiWXlKelQFtkJmwyRfKv0povLSR7bC61VcpxCPM2x8B
UIjEt80rv8Qz3D72MJMm8enm6IN85wB0EE5OoOUt+US6CaJ0OjoIzPHGfHQnCIN7
1ugWQAbecW3MtwYk960lFjTHThPTIEA4CagGsFc0cTNjubB/US18ADkovi/FFQsQ
PvnmrvMrSQAylVFdiDcJzGcAzHup1zJlGiGt6volqo9AOPTkzLYYDbEcnSDfgrOD
wFsGU3KCA5ep6C80mz4NGJN4CumEbpGUTLWNrySiFZKaka3nZqqpcF9FnTWf3mzB
aHRsoOZBAgMBAAECggEAe1QzVGahwz/1pYnbAg1Igk/IamI+io3moHKkV5kfub6t
NEf6WiS4R/1ixxJZLYRmyb1QaBI2MdmTI6mi30IWuC3U3n402NA3eY7N5hb+Mz4i
pI6J3OkcYJzcFIBwRMcrDdP+IUhVHxVP9EH2/eh/5NW55RtEN+b/hFjSGXmnJPTW
ICS1qHyXTWmiKgVSw1VS6QwvEmVzfBeXuPZMvMFweUV2CMHhgDkNUGRkX2mIpFW9
3l4x9VVuiZjtx13i6FPZoFYx2kGicWLGnTNkqvLZAazNvJp8ztvQzEEQKwHwLyw9
jwg8fAxLio1GhAMzgOvBhyRpyM4J0dFBn71EphGJ2QKBgQDwRVpNuGs2ex9ZM00J
lqBSHRrFW7i1OcGdgcJuw5HHWSJelDHN+hrJNTBlO401ItPOnrdfjvASkswk7nG+
/RzGxUIh/x7NeDxohAqfLzy6uln/RdYVoeT23fkSCrMiy3fVW5P3eSoI2TZZRX+b
IAAEJSOTgJmLH2oXOL5I6ZQFtwKBgQDRzoSn+QKOcYojA29BDmLbTlYzzn1z2UFq
u+p9UnNx4cGMQx5Oktl0gejtmgBFGy/utSJUOsztSvK6ABOpLJZ9Exrg+l7TN1e0
1tuuDfOauaSiZgpIUQiVGFWTsDbc6A/wtBORPCtZfMBukzEi210a7eQiitM58GM/
nHSBVfszxwKBgGuzmswV67ErNZ0letXeeBT2yOZIvB44Oorg/IfsEG+ci+R7Z2ve
PZ2NwxjNvflgmDMZQDeMeh7JQMsZO1GSYhDToVZd5q/RwrpS3fQHF6DYIblk05c0
z869J4Wn2C6zqA6ykzwuSuJWg582oQGnMXqqLy1SSwFq3oJ0RA+o7Fo3AoGBAJ4R
CFKAwVNN6TOt38DUtNfi8gD//fYs5SMjxmt6le1jl200F/48lsY3JaT01GU8MWWX
Y/CviDryr2JAso9PP2Wl4idDmfNpi5N8GG/OpQyZ9pY/aFnJazzg44BsTzkpQPEo
ymEuQr6dxWDJVkibmk6ykaEQlEjfefavyfqzK5l7AoGBAJNXeBiFInqQa3ON14aM
zkzPRbd02Do9U1540IDXc26SHQKmwdVmrKoKLnvJMvMPoiHTG6cavApQOJJ6Dl4e
+mAtGgRyylOddsHifX5ax7FZbBIIouGzhZXmnfX+qE/6+irdznZv7N9K9ngh49ww
D77x+/g4QAjnjW/B66X36dM2
-----END PRIVATE KEY-----
```

**注意**：
- 必须保持多行格式
- 包含完整的 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`
- 在 Vercel 输入时，直接粘贴整个内容（包括换行符）

---

### 微信支付平台证书（新增 - 重要！）

```bash
WECHAT_PLATFORM_CERT=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwc5it+8b+M0lO4gJHpT2
3Qx4AqWq7Fc5xNfU8PSi03dHNLPQ91NLdR1lIXeRunRrinYlmqW6j/kImK3fFmyR
JJGJh0Ip3OtERTlUJGAS9QqJ90gAzww3QWTvR+4dkK1KIx5a5dL+v2mSYG6pHCHr
LrrJ8DxaZMOAvIVX63HkTei4Xd71JePUaxgyP69D9XNLSK8RxfQhj42OGh/LBwoG
PCffM6R0bJdUFHYmeQZDd0W3ubLZUDdQhfpzwAV4uBml6IuIJjffCEBXfmTx1+PY
XfgWbLzHULLKZWMbYCrt/X/luBWJwDkw5AZRu7+/N1/1Sgl0caEakzZWHD14Ml3U
rwIDAQAB
-----END PUBLIC KEY-----

WECHAT_PLATFORM_CERT_SERIAL_NO=PUB_KEY_ID_0115863209012025112900381718000801
```

**注意**：
- 必须保持多行格式
- 包含完整的 `-----BEGIN PUBLIC KEY-----` 和 `-----END PUBLIC KEY-----`

---

## 🟡 网站配置

```bash
SITE_URL=https://myshop.fyyd.net
WECHAT_PAY_NOTIFY_URL=https://myshop.fyyd.net/payment/notify/
PAYMENT_TEST_MODE=True
```

**⚠️ 关于测试模式：**
- 当前建议设置为 `True`（启用测试模式）
- 测试模式下，系统会模拟支付成功，不调用真实微信支付 API
- 等解决微信支付平台证书问题后，再改为 `False`
- 详见下方"关于微信支付平台证书问题"部分

---

## 🔵 可选配置（邮件功能）

如果需要发送邮件通知，配置以下变量：

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@myshop.fyyd.net
```

---

## 📋 配置检查清单

在 Vercel 环境变量页面，确认以下变量都已设置：

- [ ] `DATABASE_URL` - PostgreSQL 连接字符串
- [ ] `SECRET_KEY` - Django 密钥（50+ 字符）
- [ ] `DEBUG` - 设为 `False`
- [ ] `WECHAT_APP_ID` - 微信公众号 AppID
- [ ] `WECHAT_APP_SECRET` - 微信公众号 AppSecret
- [ ] `WECHAT_MCH_ID` - 微信支付商户号
- [ ] `WECHAT_API_V3_KEY` - 微信支付 API v3 密钥
- [ ] `WECHAT_SERIAL_NO` - 微信支付证书序列号
- [ ] `WECHAT_PRIVATE_KEY` - 微信支付私钥（多行）
- [ ] `WECHAT_PLATFORM_CERT` - 微信支付平台证书（新增）
- [ ] `WECHAT_PLATFORM_CERT_SERIAL_NO` - 平台证书序列号（新增）
- [ ] `SITE_URL` - 网站 URL
- [ ] `WECHAT_PAY_NOTIFY_URL` - 微信支付回调 URL
- [ ] `PAYMENT_TEST_MODE` - 设为 `True`（暂时启用测试模式）

---

## ⚠️ 常见错误

### 错误 1：DATABASE_URL 特殊字符编码错误
**错误示例**：
```bash
postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@...  # ❌ 错误
```

**正确示例**：
```bash
postgresql://postgres:uku!xpt@EBY1wzb-mwu@...  # ✅ 正确
```

### 错误 2：WECHAT_PRIVATE_KEY 格式错误
**错误**：将多行私钥压缩成单行
**正确**：保持原始的多行格式，包含所有换行符

### 错误 3：SECRET_KEY 太简单
**错误**：使用默认的 `django-insecure-...`
**正确**：生成新的强随机密钥

---

## 🔄 配置完成后

1. 保存所有环境变量
2. 在 Vercel 项目中点击 **Redeploy**（重新部署）
3. 等待部署完成（2-3 分钟）
4. 检查 Function Logs 确认没有错误

---

## 📞 获取帮助

如果部署仍然失败，请检查 Vercel 的 **Function Logs**，查找以下信息：
- `[INIT] DATABASE_URL: SET (length: XXX)` - 确认 DATABASE_URL 已设置
- 数据库连接错误的详细信息
- 任何 Python 异常堆栈跟踪

---

## 🔧 关于微信支付平台证书问题

### 当前状态

经过诊断，你的微信支付配置是**正确的**：
- ✅ 商户证书序列号：正确（40位十六进制）
- ✅ 商户私钥：格式正确（RSA 2048位）
- ✅ APIv3密钥：正确（32字符）
- ✅ 签名功能：正常
- ✅ Native 支付：已开通

### 遇到的问题

调用微信支付 `/v3/certificates` API 下载平台证书时返回 404 错误：
```
{
  "code": "RESOURCE_NOT_EXISTS",
  "message": "无可用的平台证书，请在商户平台-API安全申请使用微信支付公钥"
}
```

### 临时解决方案（当前采用）

启用**支付测试模式**：
- 将 `PAYMENT_TEST_MODE` 设为 `True`
- 系统会跳过真实微信支付 API 调用
- 订单会自动模拟支付成功
- 可以正常测试整个支付流程

### 长期解决方案

需要联系微信支付技术支持，提供以下信息：

**问题描述**：
- 商户号：1586320901
- 问题：无法通过 API 下载微信支付平台证书
- 错误代码：404 RESOURCE_NOT_EXISTS
- 已确认：Native 支付已开通，API 证书已申请，所有配置正确

**可能的原因**：
1. 商户号需要完成额外的审核或认证流程
2. Native 支付产品需要完全激活（可能需要几天时间）
3. 需要在商户平台手动"申请"或"启用"平台证书下载权限
4. 账户可能有限制或欠费状态

**微信支付技术支持**：
- 在线客服：登录商户平台，点击右下角"咨询客服"
- 官方文档：https://pay.weixin.qq.com/doc/v3/merchant/4012153196
- 商户平台：https://pay.weixin.qq.com

### 何时切换回真实支付

等收到微信支付技术支持的确认，或者能成功下载平台证书后：
1. 重新运行诊断脚本：`python3 download_platform_cert_direct.py`
2. 确认能成功下载平台证书
3. 将平台证书更新到 Vercel 环境变量
4. 将 `PAYMENT_TEST_MODE` 改为 `False`
5. 重新部署
