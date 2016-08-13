# -*- coding: utf-8 -*-
import os
import six
import string
import random
import time
import hashlib

from django.conf import settings

from wechat_sdk import WechatConf
from django.core.cache import caches
cache = caches['default']



# 获取view中get方法的参数公共方法
def get_get_args(request, *args):
    get_args = []
    for item in args:
        get_args.append(request.GET.get(item, None))

    return get_args


def get_nonce_str(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in xrange(length))


def get_timestamp():
        return int(time.time())


def sign_js_wechat_config(config):
    ret = []
    for key in sorted(config.keys()):
        if (key != 'signature') and (key != '') and (config[key] is not None):
            ret.append('%s=%s' % (key.lower(), config[key]))
    sign_string = '&'.join(ret)
    config['signature'] = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()



####################################
# 微信订阅号开发 #
# 获取配置文件＆＆管理各种token #
####################################
def get_wechat_conf(appid=None, appsecret=None, token=None, encoding_aes_key=None, encrypt_mode='normal', **kwargs):
    # 从缓存中获取各种token
    access_token = cache.get('wechat_access_token_%s' % appid)
    access_token_expires_at = cache.get('wechat_access_token_expires_at_%s' % appid)
    jsapi_ticket = cache.get('wechat_jsapi_ticket_%s' % appid)
    jsapi_ticket_expires_at = cache.get('wechat_jsapi_ticket_expires_at_%s' % appid)

    # 配置
    conf = WechatConf( 
        token=token, 
        appid=appid, 
        appsecret=appsecret, 
        encrypt_mode=encrypt_mode,  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
        encoding_aes_key=encoding_aes_key, # 如果传入此值则必须保证同时传入 token, appid
        access_token=access_token,
        access_token_expires_at=access_token_expires_at,
        jsapi_ticket=jsapi_ticket,
        jsapi_ticket_expires_at=jsapi_ticket_expires_at,
    )

    # 获取最新的token，设置缓存（上一步配置的时候，如果没有过期，还是得到原来的token）
    access_token_newest = conf.get_access_token()
    cache.set('wechat_access_token_%s' % appid, access_token_newest.get('access_token'))
    cache.set('wechat_access_token_expires_at_%s' % appid, access_token_newest.get('access_token_expires_at'))
    jsapi_ticket_newest = conf.get_jsapi_ticket()
    cache.set('wechat_jsapi_ticket_%s' % appid, jsapi_ticket_newest.get('jsapi_ticket'))
    cache.set('wechat_jsapi_ticket_expires_at_%s' % appid, jsapi_ticket_newest.get('jsapi_ticket_expires_at'))

    return conf



def get_wechat_config(name, default=None):
    """
    Get configuration variable from environment variable
    or django setting.py
    """
    config = os.environ.get(name, getattr(settings, name, default))
    if config is not None:
        if isinstance(config, six.string_types):
            return config.strip()
        else:
            return config
    else:
        return None