# -*- coding:utf-8 -*-
"""
对于第三方包wechat_sdk的功能扩展
"""
import json
import requests
import six
from wechat_sdk import WechatBasic
from wechat_sdk.lib.request import WechatRequest




class WechatRequestExtension(WechatRequest):
    """ 
    修改WechatRequest对传过去的参数access_token的处理（原始默认是使用账号的access_token，而微信网页相关接口需要直接使用网页的access_token）
    """
    def __init__(self, conf=None):
        """
        :param conf: WechatConf 配置类实例
        """
        self.__conf = conf

    def request(self, method, url, access_token=None, **kwargs):
        """
        向微信服务器发送请求
        :param method: 请求方法
        :param url: 请求地址
        :param access_token: access token 值, 如果初始化时传入 conf 会自动获取, 如果没有传入则请提供此值
        :param kwargs: 附加数据
        :return: 微信服务器响应的 JSON 数据
        """
        access_token = self.__conf.access_token if self.__conf is not None else access_token
        if "params" not in kwargs:
            kwargs["params"] = {
                "access_token": access_token
            }
        elif 'access_token' not in  kwargs["params"]:
            kwargs["params"]["access_token"] = access_token

        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            if isinstance(body, six.text_type):
                body = body.encode('utf8')
            kwargs["data"] = body

        r = requests.request(method=method, url=url, **kwargs )
        r.raise_for_status()

        ######## 此处注意，微信js相关接口返回的response的encoding有误，导致r.json()编码错误
        # 使用r.encoding = None解决
        try:
            r.encoding = None
            response_json = r.json()
        except ValueError:  # 非 JSON 数据
            return r

        headimgurl = response_json.get('headimgurl')
        if headimgurl:
            response_json['headimgurl'] = headimgurl.replace('\\', '')
        self._check_official_error(response_json)
        return response_json





class WechatBasicExtension(WechatBasic):
    """
    新增一些sdk没有的功能
    """

    def get_js_authorization_redirect_url(self, redirect_uri, scope='snsapi_userinfo', state=''):
        """
        微信网页授权流程第一步：用户同意授权，获取code
        返回：用户授权回调url
        """
        if not redirect_uri:
            raise ValueError('Parameter redirect_uri is not valid')
        return 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect' % (self.conf.appid, redirect_uri, scope, state, )

    def get_js_authorization_access_token(self, code):
        """
        微信网页授权流程第二步：通过code换取网页授权access_token
        :param code 填写第一步获取的code参数
        :return: access_token    网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        :return: expires_in  access_token接口调用凭证超时时间，单位（秒）
        :return: refresh_token   用户刷新access_token
        :return: openid  用户唯一标识，请注意，在未关注公众号时，用户访问公众号的网页，也会产生一个用户和公众号唯一的OpenID
        :return: scope   用户授权的作用域，使用逗号（,）分隔
        """
        return self.request.get(
            url='https://api.weixin.qq.com/sns/oauth2/access_token',
            params={
                'appid': self.conf.appid,
                'secret': self.conf.appsecret,
                'code': code,
                'grant_type': 'authorization_code',
            }
        )

    def get_js_authorization_refresh_token(self, refresh_token):
        """
        微信网页授权流程第三步：刷新access_token（如果需要）
        :param refresh_token 填写通过access_token获取到的refresh_token参数  
        :return: access_token    网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        :return: expires_in  access_token接口调用凭证超时时间，单位（秒）
        :return: refresh_token   用户刷新access_token
        :return: openid  用户唯一标识，请注意，在未关注公众号时，用户访问公众号的网页，也会产生一个用户和公众号唯一的OpenID
        :return: scope   用户授权的作用域，使用逗号（,）分隔
        """

        return self.request.get(
            url='https://api.weixin.qq.com/sns/oauth2/refresh_token',
            params={
                'appid': self.conf.appid,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
        )

    def get_js_authorization_user_info(self, access_token, openid, lang='zh_CN'):
        """
        微信网页授权流程第四步：拉取用户信息(需scope为 snsapi_userinfo)
        :param access_token 网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        :param openid   用户的唯一标识
        :return: 返回的 JSON 数据包
        """
        # 注意此处要使用到jsSDK的access_token,则使用扩展的WechatRequestExtension
        request = WechatRequestExtension(conf=self.conf)
        return request.get(
            url='https://api.weixin.qq.com/sns/userinfo',
            params={
                'access_token': access_token,
                'openid': openid,
                'lang': lang,
            }
        )



