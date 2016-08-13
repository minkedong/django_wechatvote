# -*- coding:utf-8 -*-
import codecs
import os
import sys

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()



NAME = "django_wechatvote"

PACKAGES = find_packages()

REQUIRES = ['Django==1.8.2', 'requests', 'wechat-sdk', 'django-tastypie==0.12.2', 'qiniu', 'Pillow']

DESCRIPTION = "this is a package for django wechat vote"


KEYWORDS = "django vote wechat"

AUTHOR = "minkedong"

AUTHOR_EMAIL = "minkedong89@126.com"

URL = "https://github.com/minkedong/django_wechatvote"

VERSION = "0.0.5"

LICENSE = "Free"

LONG_DESCRIPTION = """
django_wechatvote

***微信投票活动***

文档地址：

http://blog.08050142.com/2016/08/12/django-wechatvote/

"""


setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    install_requires = REQUIRES,
    include_package_data=True,
    zip_safe=True,
)