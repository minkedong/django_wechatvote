# -*- coding: utf-8 -*-
"""
微信公众号实用修饰器
"""
from django.http import HttpResponseRedirect

from wechat_api import WeChatApi
from wechat_conf import WECHAT_APPID, WECHAT_APPSECRET, WECHAT_JS_DOMAIN, WECHAT_TOKEN, WECHAT_ENCODING_AES_KEY, WECHAT_MODE
from wechat_utils import get_get_args

# a decorator, used on any view that needs user_info
# user_info will be passed as a key word argument to the view
# NOTE:
# user_info may be None if the given params are wrong,
# since there has not a global solution to indicate what to do at this situation,
# the judgement is left to the view to handle.
# 微信网页授权,　获取用户信息
def require_wechat_authorization(appid=None, appsecret=None, js_domain=None, token=None, encoding_aes_key=None, encrypt_mode=None):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            wechat_api = WeChatApi(
                appid = appid or WECHAT_APPID,
                appsecret =appsecret or WECHAT_APPSECRET,
                js_domain =js_domain or WECHAT_JS_DOMAIN,
                token =token or WECHAT_TOKEN,
                encoding_aes_key = encoding_aes_key or WECHAT_ENCODING_AES_KEY,
                encrypt_mode = encrypt_mode or WECHAT_MODE
            )
            identify = request.get_signed_cookie('identify', default=None, salt='js_authorization')
            cached_userinfo = wechat_api.get_js_user_info_by_openid(identify) if identify else None
            user_info = None
            if not cached_userinfo:
                code, state = get_get_args(request, 'code', 'state')
                if not state or state != 'authorized':
                    redirect_uri = '%s://%s%s' % (request.scheme, wechat_api.js_domain, request.path)
                    authorization_redirect_url = wechat_api.wechat_basic.get_js_authorization_redirect_url(redirect_uri, scope='snsapi_userinfo', state='authorized')
                    return HttpResponseRedirect(authorization_redirect_url)
                user_info = wechat_api.get_js_user_info_by_code(code)
            else :
                user_info = cached_userinfo
            kwargs.update({'wechat_user_info': user_info})
            response = func(request, *args, **kwargs)
            response.set_signed_cookie('identify', value=user_info['openid'], salt='js_authorization')
            return response
        return wrapper
    return decorator


# 获取wechat　config,作为前台wx.config使用
def require_wechat_config(appid=None, appsecret=None, js_domain=None, token=None, encoding_aes_key=None, encrypt_mode=None):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            wechat_api = WeChatApi(
                appid = appid or WECHAT_APPID,
                appsecret =appsecret or WECHAT_APPSECRET,
                js_domain =js_domain or WECHAT_JS_DOMAIN,
                token =token or WECHAT_TOKEN,
                encoding_aes_key = encoding_aes_key or WECHAT_ENCODING_AES_KEY,
                encrypt_mode = encrypt_mode or WECHAT_MODE
            )
            wechat_config = wechat_api.get_js_wechat_config(request.get_full_path())
            kwargs.update({'wechat_config':wechat_config})
            response = func(request, *args, **kwargs)
            return response
        return wrapper
    return decorator