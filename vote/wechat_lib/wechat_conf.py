# -*- coding: utf-8 -*-
from wechat_utils import get_wechat_config

WECHAT_APPID = get_wechat_config('WECHAT_APPID')
WECHAT_APPSECRET = get_wechat_config('WECHAT_APPSECRET')
WECHAT_JS_DOMAIN = get_wechat_config('WECHAT_JS_DOMAIN')
WECHAT_TOKEN = get_wechat_config('WECHAT_TOKEN')
WECHAT_ENCODING_AES_KEY = get_wechat_config('WECHAT_ENCODING_AES_KEY')
WECHAT_MODE = get_wechat_config('WECHAT_MODE', 'normal')