# Vercel 部署指南

本项目已配置为可在 Vercel 上部署。以下是详细的部署步骤。

## ⚠️ 重要提示

**Vercel 不支持 SQLite**，因为其文件系统是只读的。**必须配置 PostgreSQL 数据库**（推荐使用 Supabase）。

## 📋 部署前准备

### 1. 配置 Supabase 数据库

1. 访问 [Supabase](https://supabase.com) 并创建项目
2. 获取数据库连接字符串（PostgreSQL URL）
3. 格式：`postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`

### 2. 准备环境变量

需要在 Vercel 控制台配置以下环境变量：

```env
# Django 基础配置
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# 微信公众号配置
WECHAT_APP_ID=wx2f5f0f2135ea10d4
WECHAT_APP_SECRET=88c62413dcdb58ee63348b2ba2465246

# 微信支付配置
WECHAT_MCH_ID=1586320901
WECHAT_API_V3_KEY=xgWzZEMZbzrW0syJLghqLuvZCR1ej3kQ
WECHAT_SERIAL_NO=78CE472193EC6C6B270550B62882FB87D9F0E980
WECHAT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
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
-----END PRIVATE KEY-----"

# 网站配置
SITE_URL=https://myshop.fyyd.net
WECHAT_PAY_NOTIFY_URL=https://myshop.fyyd.net/payment/notify/

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@myshop.fyyd.net

# 支付测试模式（生产环境设为 False）
PAYMENT_TEST_MODE=False
```

## 🚀 部署步骤

### 1. 推送代码到 Git 仓库

```bash
git add .
git commit -m "配置 Vercel 部署"
git push origin main
```

### 2. 在 Vercel 上导入项目

1. 访问 [Vercel](https://vercel.com)
2. 点击 **"Add New Project"**
3. 导入你的 Git 仓库
4. 配置项目：
   - **Framework Preset**: Other
   - **Root Directory**: 保持默认（留空）
   - **Build Command**: 留空（使用 vercel.json 配置）
   - **Output Directory**: 留空

### 3. 配置环境变量

在 Vercel 项目设置中：

1. 进入 **Settings** → **Environment Variables**
2. 添加上述所有环境变量
3. **重要**：`WECHAT_PRIVATE_KEY` 需要保持多行格式，直接粘贴包含换行符的完整私钥

### 4. 配置自定义域名

1. 在 Vercel 项目中进入 **Settings** → **Domains**
2. 添加域名 `myshop.fyyd.net`
3. 按照 Vercel 提示配置 DNS 记录

### 5. 部署

点击 **Deploy** 按钮，Vercel 会自动：
- 安装依赖
- 收集静态文件
- 部署应用

## 🔧 部署后配置

### 1. 运行数据库迁移

部署成功后，需要手动运行数据库迁移：

**方式 1：使用 Vercel CLI**
```bash
vercel env pull .env.production
cd django_shop
python manage.py migrate
python manage.py createsuperuser
```

**方式 2：在本地连接生产数据库**
```bash
# 设置生产数据库 URL
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
cd django_shop
python manage.py migrate
python manage.py createsuperuser
```

### 2. 验证微信公众号域名

访问：`https://myshop.fyyd.net/MP_verify_ppTG1CEXB5Ni8Hc5.txt`
应该看到：`ppTG1CEXB5Ni8Hc5`

### 3. 配置微信支付商户平台

1. 登录 [微信支付商户平台](https://pay.weixin.qq.com)
2. 配置支付回调地址：`https://myshop.fyyd.net/payment/notify/`

## ⚠️ 常见问题

### 1. 数据库连接失败

**原因**：未配置 `DATABASE_URL` 环境变量

**解决**：在 Vercel 环境变量中添加 Supabase 数据库连接字符串

### 2. 静态文件 404

**原因**：静态文件未收集

**解决**：Vercel 会自动收集，如果有问题，检查 `vercel.json` 配置

### 3. 微信支付回调失败

**原因**：
- 回调 URL 配置错误
- 签名验证失败
- 环境变量未正确配置

**解决**：
- 检查 `WECHAT_PAY_NOTIFY_URL` 环境变量
- 确保私钥格式正确（保持换行符）
- 查看 Vercel 函数日志

### 4. Vercel 函数超时

**原因**：免费版 Vercel 函数执行时间限制为 10 秒

**解决**：
- 升级到 Pro 版本（60 秒）
- 优化代码性能
- 将耗时操作改为异步

## 📊 监控和日志

### 查看部署日志
在 Vercel 项目页面 → **Deployments** → 点击具体部署 → 查看日志

### 查看函数日志
在 Vercel 项目页面 → **Logs** → 实时查看函数执行日志

## 🔐 安全建议

1. **生产环境设置**：
   - `DEBUG=False`
   - 使用强密码的 `SECRET_KEY`
   - 配置正确的 `ALLOWED_HOSTS`

2. **数据库安全**：
   - 定期备份 Supabase 数据库
   - 使用强密码
   - 限制数据库访问 IP

3. **API 密钥保护**：
   - 不要将密钥提交到 Git
   - 定期轮换 API 密钥
   - 使用 Vercel 环境变量存储

## 📝 更新部署

每次推送到 Git 仓库的 main 分支，Vercel 会自动重新部署。

```bash
git add .
git commit -m "更新内容"
git push origin main
```

## 🆘 获取帮助

- [Vercel 文档](https://vercel.com/docs)
- [Django on Vercel 示例](https://github.com/vercel/examples/tree/main/python/django)
- [Supabase 文档](https://supabase.com/docs)
