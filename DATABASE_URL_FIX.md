# DATABASE_URL 配置修复指南

## ⚠️ Vercel + Supabase 数据库连接问题

如果您看到数据库连接错误：`ensure_connection self.connect()`，请按以下步骤修复。

---

## 🔴 方案 1：在 DATABASE_URL 末尾添加 SSL 参数（推荐）

在 Vercel 环境变量中，将 `DATABASE_URL` 修改为：

```
postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres?sslmode=require
```

**关键变化**：
- 在 URL 末尾添加了 `?sslmode=require`
- 密码保持 URL 编码：`uku%21xpt%40EBY1wzb-mwu`（`!` → `%21`, `@` → `%40`）

---

## 🟡 方案 2：使用 prefer 模式（如果方案 1 失败）

如果 `sslmode=require` 仍然失败，尝试使用 `prefer` 模式：

```
postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres?sslmode=prefer
```

---

## 🟢 方案 3：从 Supabase 获取直接连接字符串

1. 登录 [Supabase 控制台](https://supabase.com/dashboard)
2. 选择您的项目：`gcbqmhkxqopfaoexecnl`
3. 进入 **Settings** → **Database**
4. 找到 **Connection String** → **URI** → **Use connection pooling**
5. 复制完整的连接字符串（已包含 SSL 参数）

**示例格式**：
```
postgres://postgres.gcbqmhkxqopfaoexecnl:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

然后在这个字符串中：
- 将 `[PASSWORD]` 替换为：`uku%21xpt%40EBY1wzb-mwu`（URL 编码后的密码）
- 确保使用的是 **connection pooler** 端口（6543），而不是直连端口（5432）

---

## 📋 完整的 Vercel 环境变量配置

### 必需配置

```bash
# 数据库连接（使用方案 1）
DATABASE_URL=postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres?sslmode=require

# Django 基础
SECRET_KEY=（您生成的随机密钥，50+ 字符）
DEBUG=False

# 微信公众号
WECHAT_APP_ID=wx2f5f0f2135ea10d4
WECHAT_APP_SECRET=88c62413dcdb58ee63348b2ba2465246

# 微信支付
WECHAT_MCH_ID=1586320901
WECHAT_API_V3_KEY=xgWzZEMZbzrW0syJLghqLuvZCR1ej3kQ
WECHAT_SERIAL_NO=78CE472193EC6C6B270550B62882FB87D9F0E980
WECHAT_PRIVATE_KEY=（完整的多行私钥）

# 网站配置
SITE_URL=https://myshop.fyyd.net
WECHAT_PAY_NOTIFY_URL=https://myshop.fyyd.net/payment/notify/
PAYMENT_TEST_MODE=False
```

---

## 🔍 验证配置

部署后，在 Vercel Function Logs 中应该看到：

```
[INIT] Initializing Django WSGI application...
[INIT] DATABASE_URL: SET (length: XXX)
[INIT] DEBUG: False
[INIT] DB User: postgres
[INIT] DB Host: db.gcbqmhkxqopfaoexecnl.supabase.co:5432
[INIT] DB Name: postgres?sslmode=require
[INIT] Password length: 24
[INIT] ✅ WSGI application initialized successfully
```

**如果仍然失败**，日志会显示详细的错误信息和 traceback。

---

## 💡 密码编码规则

您的原始密码：`uku!xpt@EBY1wzb-mwu`

**URL 编码后**：`uku%21xpt%40EBY1wzb-mwu`

编码规则：
- `!` → `%21`
- `@` → `%40`
- 其他字符保持不变

⚠️ **注意**：在 Vercel 环境变量中直接粘贴 URL 编码后的密码，不需要额外的引号或转义。

---

## 🆘 如果所有方案都失败

请提供以下信息：

1. Vercel Function Logs 的完整输出（特别是 `[INIT]` 和 `[ERROR]` 部分）
2. Supabase 项目的区域（Region）
3. 是否启用了 Connection Pooling

可能需要：
- 检查 Supabase 数据库防火墙设置
- 确认 Vercel 的 IP 地址未被阻止
- 尝试使用 Supabase 的 Connection Pooler（端口 6543）
