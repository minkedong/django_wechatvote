# -*- coding: utf-8 -*-
from tastypie.api import Api
from django.conf.urls import patterns, include, url

from vote.modelsResource import *


v1_api = Api(api_name='v1/vote')
v1_api.register(VoteProductResource())


urlpatterns = [
    url(r'^v1/vote/createproduct/$', 'vote.views.vote_create_product'),
    url(r'^v1/vote/submit/$', 'vote.views.vote_submit'),
]