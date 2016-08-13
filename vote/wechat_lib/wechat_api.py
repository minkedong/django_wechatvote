# -*- coding: utf-8 -*-
import logging
from django.core.cache import caches

from wechat_sdk_extension import WechatBasicExtension
from wechat_utils import get_nonce_str, get_timestamp, sign_js_wechat_config, get_wechat_conf

cache = caches['default']
logger = logging.getLogger(__name__)




class WeChatApi(object):
    """
    微信公众号业务类
    """

    def __init__(self, appid, appsecret, js_domain=None, token=None, encoding_aes_key=None, encrypt_mode='normal'):
        self.js_domain = js_domain
        self.wechat_basic = WechatBasicExtension(get_wechat_conf(appid, appsecret, token, encoding_aes_key, encrypt_mode))


    def get_js_user_info_by_openid(self, openid):
        appId = self.wechat_basic.conf.appid
        cached_userinfo = cache.get('%s_%s_userinfo'%(appId, openid))
        if cached_userinfo:
            return cached_userinfo
        cached_openid_json = cache.get('%s_%s_openid'%(appId, openid))
        if not cached_openid_json:
            return None
        refresh_token = cached_openid_json['refresh_token']

        openid_json = self.wechat_basic.get_js_authorization_refresh_token(refresh_token)
        if openid_json.has_key('errcode'):
            logger.error('error when getting openid: %s, %s' %
                          (openid_json['errcode'], openid_json['errmsg']))
            return None

        # dont cache openid here, we don't know exact expire time for refresh_token here
        userinfo_json = self.wechat_basic.get_js_authorization_user_info(openid_json['access_token'], openid_json['openid'])
        if userinfo_json.has_key('errcode'):
            logger.error('error when getting userinfo: %s, %s' %
                          (userinfo_json['errcode'], userinfo_json['errmsg']))
            return None
        cache.set('%s_%s_userinfo'%(appId, openid_json['openid']), userinfo_json, timeout=int(openid_json['expires_in'])) # 7200s, 2h

        return userinfo_json


    # 网页授权流程
    # 1. 前端访问授权url获得code （见require_wechat_authorization）
    # 2. 使用code和appid与secret获取openid和access_token， appid与secret必须用服务号的，这里的access_token是特定的，不同于缓存里调用接口所用的token
    # 3. 使用2里获得的access_token和openid获取个人信息
    # 返回参数结构见
    # https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842&token=&lang=zh_CN
    # 需要注意的是授权的回调url不支持参数
    def get_js_user_info_by_code(self, code):
        appId = self.wechat_basic.conf.appid

        openid_json = self.wechat_basic.get_js_authorization_access_token(code)
        if openid_json.has_key('errcode'):
            logger.error('error when getting openid: %s, %s' %
                          (openid_json['errcode'], openid_json['errmsg']))
            return None

        cache.set('%s_%s_openid'%(appId,openid_json['openid']), openid_json, timeout=2592000) #30days
        cached_userinfo = cache.get('%s_%s_userinfo'%(appId, openid_json['openid']))
        if cached_userinfo:
            return cached_userinfo

        userinfo_json = self.wechat_basic.get_js_authorization_user_info(openid_json['access_token'], openid_json['openid'])
        if userinfo_json.has_key('errcode'):
            logger.error('error when getting userinfo: %s, %s' %
                          (userinfo_json['errcode'], userinfo_json['errmsg']))
            return None
        cache.set('%s_%s_userinfo'%(appId, openid_json['openid']), userinfo_json, timeout=int(openid_json['expires_in'])) # 7200s, 2h

        return userinfo_json


    def get_js_wechat_config(self, full_path):
        ret = {
            'nonceStr': get_nonce_str(15),
            'jsapi_ticket': self.wechat_basic.conf.jsapi_ticket,
            'timestamp': get_timestamp(),
            'url': 'http://%s%s' % (self.js_domain, full_path, ),
        }
        sign_js_wechat_config(ret)
        ret['appId'] = self.wechat_basic.conf.appid
        return ret