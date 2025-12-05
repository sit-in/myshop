# Vercel 快速部署指南

## 🚀 部署到 Vercel

### 步骤 1：准备 Supabase 数据库

1. 访问 [Supabase](https://supabase.com)
2. 使用你的 myshop 项目
3. 获取数据库连接字符串（已配置）：
   ```
   postgresql://postgres:uku!xpt@EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres
   ```

### 步骤 2：在 Vercel 上导入项目

1. 访问 [Vercel](https://vercel.com)
2. 点击 **"Add New"** → **"Project"**
3. 导入你的 Git 仓库：`https://github.com/sit-in/myshop.git`
4. **Framework Preset**: 选择 **"Other"**
5. **Root Directory**: 留空
6. 点击 **"Deploy"** 按钮（先不配置环境变量也可以部署）

### 步骤 3：配置环境变量

部署完成后，进入项目设置：

1. 进入 **Settings** → **Environment Variables**
2. 添加以下环境变量（**注意：密码中的特殊字符需要 URL 编码**）：

```env
# ===== 必需配置 =====

# Django 配置
SECRET_KEY=django-insecure-change-this-in-production-use-your-own-secret-key
DEBUG=False

# Supabase 数据库 (特殊字符已编码: ! -> %21, @ -> %40)
DATABASE_URL=postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres

# ===== 微信公众号配置 =====
WECHAT_APP_ID=wx2f5f0f2135ea10d4
WECHAT_APP_SECRET=88c62413dcdb58ee63348b2ba2465246

# ===== 微信支付配置 =====
WECHAT_MCH_ID=1586320901
WECHAT_API_V3_KEY=xgWzZEMZbzrW0syJLghqLuvZCR1ej3kQ
WECHAT_SERIAL_NO=78CE472193EC6C6B270550B62882FB87D9F0E980

# 微信支付私钥 (保持换行符，直接粘贴完整内容)
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

# ===== 网站配置 =====
SITE_URL=https://myshop.fyyd.net
WECHAT_PAY_NOTIFY_URL=https://myshop.fyyd.net/payment/notify/

# 支付测试模式（生产环境设为 False）
PAYMENT_TEST_MODE=False

# ===== 邮件配置（可选）=====
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@myshop.fyyd.net
```

### 步骤 4：配置自定义域名

1. 在 Vercel 项目中进入 **Settings** → **Domains**
2. 添加域名：`myshop.fyyd.net`
3. 按照 Vercel 提示配置 DNS 记录（通常是添加 CNAME 记录）

### 步骤 5：运行数据库迁移

部署成功后，需要初始化数据库：

**方式 1：在本地连接生产数据库**
```bash
# 设置生产数据库 URL (密码特殊字符需编码)
export DATABASE_URL="postgresql://postgres:uku%21xpt%40EBY1wzb-mwu@db.gcbqmhkxqopfaoexecnl.supabase.co:5432/postgres"

cd django_shop
python3 manage.py migrate
python3 manage.py createsuperuser
```

**方式 2：使用 Vercel CLI**
```bash
npm install -g vercel
vercel login
vercel env pull .env.production
cd django_shop
python3 manage.py migrate
python3 manage.py createsuperuser
```

### 步骤 6：验证部署

1. **测试微信验证文件**：
   - 访问：`https://myshop.fyyd.net/MP_verify_ppTG1CEXB5Ni8Hc5.txt`
   - 应该看到：`ppTG1CEXB5Ni8Hc5`

2. **登录后台**：
   - 访问：`https://myshop.fyyd.net/admin`
   - 使用创建的超级用户登录

3. **添加商品和卡密**

4. **测试支付流程**：
   - 访问：`https://myshop.fyyd.net`
   - 点击购买，测试完整流程

### 步骤 7：配置微信支付商户平台

1. 登录 [微信支付商户平台](https://pay.weixin.qq.com)
2. 进入 **产品中心** → **开发配置**
3. 配置 **支付回调地址**：
   ```
   https://myshop.fyyd.net/payment/notify/
   ```
4. 在 **微信公众平台** 配置域名验证

## 🔧 常见问题

### 1. 部署失败
- 检查 `vercel.json` 配置
- 查看 Vercel 部署日志
- 确保 Python 版本兼容（3.11）

### 2. 数据库连接失败
- 确认 `DATABASE_URL` 环境变量正确
- 密码特殊字符需要 URL 编码（! → %21, @ → %40）
- 检查 Supabase 数据库是否正常运行

### 3. 微信支付错误
- 确认所有微信支付环境变量已配置
- 检查私钥格式（必须保持换行符）
- 确认证书序列号正确
- 查看 Vercel 函数日志

### 4. 静态文件 404
- 运行 `python3 manage.py collectstatic`
- 检查 `vercel.json` 中的路由配置

## 📊 监控和维护

### 查看部署日志
在 Vercel 项目页面 → **Deployments** → 点击具体部署 → 查看日志

### 查看运行时日志
在 Vercel 项目页面 → **Logs** → 实时查看函数执行日志

### 数据库备份
定期备份 Supabase 数据库：
- 在 Supabase Dashboard → **Database** → **Backups**

## 🎯 下一步

- [ ] 配置邮件服务（Gmail SMTP 或其他）
- [ ] 设置监控和告警
- [ ] 配置 CDN 加速
- [ ] 优化数据库查询性能
- [ ] 添加日志记录和分析

## 🆘 需要帮助？

- [Vercel 文档](https://vercel.com/docs)
- [Supabase 文档](https://supabase.com/docs)
- [Django on Vercel 示例](https://github.com/vercel/examples/tree/main/python/django)
