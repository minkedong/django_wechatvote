# -*- coding: utf-8 -*-
"""
微信公众号开发相关功能模块
基于django1.8、wechat_sdk0.6.3，暂时提供了一些好用的修饰器
"""
from wechat_decorators import require_wechat_authorization, require_wechat_config

__all__ = [
    'require_wechat_authorization',
    'require_wechat_config',
]