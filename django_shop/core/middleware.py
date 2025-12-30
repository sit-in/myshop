import base64
import os

from django.http import HttpResponse


class BasicAuthMiddleware:
    """
    Basic Auth 认证中间件
    通过 HTTP Basic Authentication 保护整个网站
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # 从环境变量获取认证信息
        self.username = os.environ.get('BASIC_AUTH_USERNAME', '')
        self.password = os.environ.get('BASIC_AUTH_PASSWORD', '')
        # 是否启用 Basic Auth
        self.enabled = os.environ.get('BASIC_AUTH_ENABLED', 'False').lower() in ('true', '1', 'yes')

        # 关键端点：必须绕过 Basic Auth
        self.excluded_paths = [
            '/payment/notify/',           # 微信支付回调
            '/api/cron/daily-report/',    # Vercel 定时任务
            '/api/cron/test-feishu/',     # 飞书测试端点
            '/MP_verify_ppTG1CEXB5Ni8Hc5.txt',  # 微信域名验证
        ]

        # 可选：从环境变量添加额外排除路径
        extra_exclusions = os.environ.get('BASIC_AUTH_EXCLUDE_PATHS', '')
        if extra_exclusions:
            # 格式：逗号分隔，例如 "/health/,/metrics/"
            additional_paths = [p.strip() for p in extra_exclusions.split(',') if p.strip()]
            self.excluded_paths.extend(additional_paths)

    def _is_excluded_path(self, request_path):
        """检查请求路径是否应绕过 Basic Auth"""
        for excluded in self.excluded_paths:
            if request_path.startswith(excluded):
                return True
        return False

    def __call__(self, request):
        # 调试：添加自定义头部显示中间件状态
        response = None

        # 如果未启用 Basic Auth，直接放行
        if not self.enabled:
            response = self.get_response(request)
            response['X-BasicAuth-Enabled'] = 'False'
            response['X-BasicAuth-EnvValue'] = os.environ.get('BASIC_AUTH_ENABLED', 'NOT_SET')
            return response

        # 如果未配置用户名或密码，记录警告并放行
        if not self.username or not self.password:
            print("警告: BASIC_AUTH_ENABLED=True 但未配置 BASIC_AUTH_USERNAME 或 BASIC_AUTH_PASSWORD")
            response = self.get_response(request)
            response['X-BasicAuth-Enabled'] = 'True'
            response['X-BasicAuth-CredentialsSet'] = 'False'
            return response

        # 检查路径是否在排除列表中
        if self._is_excluded_path(request.path):
            response = self.get_response(request)
            response['X-BasicAuth-Enabled'] = 'True'
            response['X-BasicAuth-Excluded'] = 'True'
            return response

        # 获取 Authorization 头
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return self._unauthorized_response()

        # 解析 Basic Auth
        try:
            auth_type, auth_string = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return self._unauthorized_response()

            # 解码 Base64
            decoded = base64.b64decode(auth_string).decode('utf-8')
            username, password = decoded.split(':', 1)

            # 验证用户名和密码
            if username == self.username and password == self.password:
                # 认证成功，继续处理请求
                response = self.get_response(request)
                response['X-BasicAuth-Enabled'] = 'True'
                response['X-BasicAuth-Authenticated'] = 'True'
                return response
            else:
                return self._unauthorized_response()

        except (ValueError, UnicodeDecodeError):
            return self._unauthorized_response()

    def _unauthorized_response(self):
        """返回 401 未授权响应"""
        response = HttpResponse('Unauthorized', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Protected Area"'
        return response
