# 数据库连接故障排查指南

## 当前错误
```
Internal Server Error: / Traceback (most recent call last):
File "/var/task/_vendor/django/db/backends/base/base.py", line 279,
in ensure_connection self.connect()
```

这是数据库连接失败的错误。以下是完整的解决方案。

---

## 🔴 方案 1：使用 Supabase Connection Pooler（强烈推荐）

Vercel Serverless Functions 应该使用 **Connection Pooler** 而不是直连。

### 步骤 1：获取 Pooler 连接字符串

1. 登录 [Supabase 控制台](https://supabase.com/dashboard)
2. 选择项目：`gcbqmhkxqopfaoexecnl`
3. 进入 **Settings** → **Database**
4. 找到 **Connection String** 部分
5. 选择 **Use connection pooling**（启用连接池）
6. 复制 **URI** 格式的连接字符串

### 步骤 2：修改 Vercel 环境变量

Connection Pooler URL 格式应该是：

```
postgresql://postgres.gcbqmhkxqopfaoexecnl:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

**注意**：
- 端口是 `6543`（Pooler 端口），而不是 `5432`（直连端口）
- 主机名包含 `pooler.supabase.com`

在 Vercel 中，将 `DATABASE_URL` 设置为：

```
postgresql://postgres.gcbqmhkxqopfaoexecnl:uku%21xpt%40EBY1wzb-mwu@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

**重要**：
- 密码仍然使用 URL 编码：`uku%21xpt%40EBY1wzb-mwu`
- 使用您在 Supabase 控制台看到的实际 pooler URL

---

## 🟡 方案 2：使用直连但禁用 SSL 验证

如果 Pooler 不可用，尝试在直连 URL 中添加 SSL 参数：

```
postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres?sslmode=disable
```

**或者使用 `prefer` 模式**：

```
postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres?sslmode=prefer
```

---

## 🟢 方案 3：检查 Vercel Function Logs

我已经在代码中添加了详细的调试日志。请按以下步骤查看：

### 步骤 1：查看 Function Logs

1. 登录 Vercel 控制台
2. 进入项目 → **Deployments**
3. 点击最新的部署
4. 点击 **Functions** 标签
5. 找到并点击 `wsgi.py` 函数
6. 查看 **Logs**

### 步骤 2：查找关键信息

在 Logs 中查找以下内容：

```
[INIT] Initializing Django WSGI application...
[INIT] DATABASE_URL: SET (length: XXX)
[INIT] DB User: postgres
[INIT] DB Host: <host:port>
[INIT] DB Name: <database>
[INIT] Password length: XX
```

**如果看到错误**：

```
[ERROR] ❌ Failed to initialize WSGI application
[ERROR] Exception type: ...
[ERROR] Exception message: ...
[ERROR] Full traceback:
...
```

**请将完整的日志发给我**，包括：
- `[INIT]` 部分的所有输出
- `[ERROR]` 部分的完整 traceback

---

## 🔵 方案 4：简化测试 - 临时禁用数据库检查

如果想先让网站运行起来，可以临时添加这个环境变量：

```
DJANGO_SETTINGS_SKIP_DB_CHECK=True
```

然后在 `settings.py` 中添加（我可以帮您添加）：

```python
if os.environ.get('DJANGO_SETTINGS_SKIP_DB_CHECK'):
    DATABASES = {}  # 临时禁用数据库
```

⚠️ **这只是为了测试，不是长期解决方案！**

---

## 📋 完整的环境变量清单（使用 Pooler）

```bash
# 方案 1：Connection Pooler（推荐）
DATABASE_URL=postgresql://postgres.gcbqmhkxqopfaoexecnl:uku%21xpt%40EBY1wzb-mwu@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# 或方案 2：直连 + sslmode=prefer
DATABASE_URL=postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres?sslmode=prefer

# 其他必需配置
SECRET_KEY=<您的密钥>
DEBUG=False
WECHAT_APP_ID=wx2f5f0f2135ea10d4
WECHAT_APP_SECRET=88c62413dcdb58ee63348b2ba2465246
WECHAT_MCH_ID=1586320901
WECHAT_API_V3_KEY=xgWzZEMZbzrW0syJLghqLuvZCR1ej3kQ
WECHAT_SERIAL_NO=78CE472193EC6C6B270550B62882FB87D9F0E980
WECHAT_PRIVATE_KEY=<完整私钥>
SITE_URL=https://myshop.fyyd.net
WECHAT_PAY_NOTIFY_URL=https://myshop.fyyd.net/payment/notify/
PAYMENT_TEST_MODE=False
```

---

## 🔍 如何获取正确的 Supabase Connection Pooler URL

### 详细步骤：

1. 访问 https://supabase.com/dashboard
2. 登录您的账号
3. 选择项目（应该能看到 `gcbqmhkxqopfaoexecnl`）
4. 左侧菜单点击 **Settings**（设置图标）
5. 点击 **Database**
6. 向下滚动到 **Connection string** 部分
7. 在 **Connection string** 下方，您会看到三个选项：
   - URI
   - JDBC
   - .NET
8. 选择 **URI**
9. **重要**：勾选 **Use connection pooling** 复选框
10. 复制显示的完整 URL

**示例格式**：
```
postgresql://postgres.gcbqmhkxqopfaoexecnl:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

11. 将 `[YOUR-PASSWORD]` 替换为：`uku%21xpt%40EBY1wzb-mwu`（URL 编码后）

**最终 URL**：
```
postgresql://postgres.gcbqmhkxqopfaoexecnl:uku%21xpt%40EBY1wzb-mwu@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

---

## ⚡ 快速测试步骤

### 测试 1：提交当前代码
```bash
git add .
git commit -m "优化数据库连接配置：禁用持久连接，适配 Serverless"
git push origin main
```

### 测试 2：尝试 Connection Pooler URL

在 Vercel 中修改 `DATABASE_URL` 为 Pooler URL（见上面步骤）

### 测试 3：查看 Logs

等待部署完成后，查看 Function Logs 中的 `[INIT]` 输出

### 测试 4：如果仍然失败

将完整的 Function Logs 发给我，包括：
- `[INIT]` 部分（显示数据库连接信息）
- `[ERROR]` 部分（显示错误详情）

---

## 🆘 常见问题

### Q1: 找不到 Connection Pooler 选项
**A**: 确保您的 Supabase 项目已启用 Connection Pooling。在项目设置中应该能看到这个选项。

### Q2: Pooler URL 的主机名是什么
**A**: 应该类似于：`aws-0-<region>.pooler.supabase.com`，端口是 `6543`

### Q3: 是否需要 sslmode 参数
**A**: 使用 Pooler 时，通常不需要额外的 SSL 参数。如果需要，可以添加 `?sslmode=require`

---

## 💡 预期的成功日志

成功连接后，Vercel Function Logs 应该显示：

```
[INIT] Initializing Django WSGI application...
[INIT] DATABASE_URL: SET (length: 150)
[INIT] DEBUG: False
[INIT] DB User: postgres.gcbqmhkxqopfaoexecnl
[INIT] DB Host: aws-0-ap-southeast-1.pooler.supabase.com:6543
[INIT] DB Name: postgres
[INIT] Password length: 24
[INIT] ✅ WSGI application initialized successfully
```

然后网站应该可以正常访问：
- https://myshop.fyyd.net/
- https://myshop.fyyd.net/admin/

---

## 📞 下一步

请按以下顺序尝试：

1. ✅ 提交我刚才修改的代码
2. 🔴 **从 Supabase 获取 Connection Pooler URL**（最重要！）
3. ✅ 在 Vercel 更新 `DATABASE_URL`
4. ✅ 等待重新部署
5. 📊 查看 Function Logs
6. 🆘 如果失败，发送日志给我

我已经优化了数据库配置，禁用了持久连接（Serverless 不适合），并添加了更智能的 SSL 处理。

**Connection Pooler 是关键**！Serverless 环境需要使用连接池，不能直连数据库。
