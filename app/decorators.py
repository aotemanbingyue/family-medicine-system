# 按角色限制接口
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(*allowed_roles):
    """要求用户角色在 allowed_roles 内，否则重定向或 403。"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in allowed_roles:
                messages.error(request, '您没有权限访问该功能。')
                return redirect('index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def role_required_ajax(*allowed_roles):
    """API 用：无权限时返回 403 JSON。"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden('未登录')
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden('无权限')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
