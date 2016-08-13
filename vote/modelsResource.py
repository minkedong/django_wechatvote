# -*- coding:utf-8 -*-
from vote.models import *
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

__all__ = ['VoteProductResource',]



####################################
# 投票排行榜接口 #
# URL: /api/v1/vote/productbrief/
####################################
class VoteProductResource(ModelResource):

    activity_id = fields.IntegerField(attribute='activity_id_id', null=True)
    image = fields.CharField(attribute='image_first_url', default='')
    slug = fields.CharField(attribute='slug', default='')

    class Meta:
        queryset = VoteProduct.objects.filter(active=True)
        resource_name = 'productbrief'
        allowed_methods = ['get']
        excludes = ['create_uid', 'write_uid', 'write_date']
        # 单页最大可以返回的数量
        max_limit = 50
        # 前台get请求不带limit参数时默认单页返回的数量
        limit = 20
        ordering = ['vote_count','create_date']
        filtering = {
            'id': ALL,
            'activity_id':ALL,
        }

    def dehydrate(self, bundle):
        """
        默认id变为rid，前台格式需求（方便其数据库使用）
        """
        if bundle.data.has_key('id'):
            bundle.data['rid'] = bundle.data.pop('id')
        return bundle