# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = [
    url(r'^activity/index/(?P<activity_id>[0-9]+)/$', 'vote.views.tmp_activity_index'),
    url(r'^product/index/(?P<product_id>[0-9]+)/$', 'vote.views.tmp_product_index'),
    url(r'^product/createform/(?P<activity_id>[0-9]+)/$', 'vote.views.tmp_product_createfrom'),
    url(r'^products/list/(?P<activity_id>[0-9]+)/$', 'vote.views.tmp_products_list'),
]