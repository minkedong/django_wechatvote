# -*- coding:utf-8 -*-
import datetime
from django.utils import timezone
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.core.files import File
from django.db import transaction
from django.db.models import Q as modelsQ, F as modelsF
from wechat_lib import require_wechat_authorization, require_wechat_config
from common import ReqParameter
from vote.models import *


__all__ = [
    'vote_create_product', 'vote_submit', 'tmp_activity_index', 
    'tmp_product_createfrom', 'tmp_product_index', 'tmp_products_list',
]



####################################
# 投票内容上传接口 #
# URL: /api/v1/vote/createproduct/
####################################
@require_wechat_authorization()
@require_http_methods(["POST"])
def vote_create_product(request, *args, **kwargs):
    info = {'status':0, 'message':'success', 'product_id':''}
    product_data = {}
    # 参数公共处理
    parameters = ReqParameter(request, [
        {'fieldname':'activity_id', 'formator':'unicode', 'option':False},
        {'fieldname':'up_user_name', 'formator':'unicode', 'option':False},
        {'fieldname':'up_user_mobile', 'formator':'unicode', 'validators':[lambda x:x.isdigit(),{'exact_length':11}], 'option':False},
        {'fieldname':'content', 'formator':'unicode', 'option':True},
        ])
    p_valid, fieldvalues = parameters.get_post_args()
    if not p_valid:
        info['status'] = 1
        info['message'] = u'参数有误'
        return JsonResponse(info, safe=False)
    activity_id, up_user_name, up_user_mobile, content = fieldvalues
    f = request.FILES.get('image')
    if not f:
        return JsonResponse({'status':1, 'message':u'请上传图片', 'product_id':''}, safe=False)

    activity = get_object_or_404(VoteActivity, id=activity_id, active=True)
    # 加入上传规则
    wechat_user_info = kwargs.get('wechat_user_info')
    openid = wechat_user_info.get('openid')
    if activity.is_endtime_active:
        if datetime.datetime.now() >= timezone.make_naive(activity.end_time):
            info['status'] = 1
            info['message'] = u'sorry,活动已截止'
            return JsonResponse(info, safe=False)
    if activity.up_product_max != 0:
        if VoteProduct.objects.filter(activity_id_id=activity.id, up_user_slug=openid).count() >= activity.up_product_max:
            info['status'] = 1
            info['message'] = u'您已达到上传上限'
            return JsonResponse(info, safe=False)

    # 正式上传作品
    product_data['activity_id_id'] = activity.id
    product_data['activity_name'] = activity.name
    product_data['up_user_name'] = up_user_name
    product_data['up_user_mobile'] = up_user_mobile
    product_data['content'] = content
    try:
        with transaction.atomic(using='default', savepoint=True):
            vote_image = VoteImage.objects.create(image=File(f))
            wechat_fields = WeChatUser._meta.get_all_field_names()
            # wechat_user = WeChatUser(**dict(filter(lambda x:x[0] in wechat_fields, wechat_user_info.items())))
            # wechat_user.save()
            wechat_user, is_created = WeChatUser.objects.get_or_create(openid=openid, defaults=dict(filter(lambda x:x[0] in wechat_fields, wechat_user_info.items())))
            product_data['wechatuser'] = wechat_user
            product_data['up_user_slug'] = openid
            vote_product = VoteProduct.objects.create(**product_data)
            vote_product.images.add(vote_image)
    except Exception, e:
        info['status'] = 1
        info['message'] = u'上传有误'
        return JsonResponse(info, safe=False)

    return JsonResponse({'status':0, 'message':u'上传成功', 'product_id':vote_product.id}, safe=False)



####################################
# 投票接口 #
# URL: /api/v1/vote/submit/
####################################
@require_wechat_authorization()
@require_http_methods(["POST"])
def vote_submit(request, *args, **kwargs):
    info = {
        'status':0,
        'message':'success',
    }
    # 参数公共处理
    parameters = ReqParameter(request, [{'fieldname':'product_id', 'formator':'unicode', 'option':False}])
    p_valid, fieldvalues = parameters.get_post_args()
    if not p_valid:
        info['status'] = 1
        info['message'] = u'参数有误'
        return JsonResponse(info, safe=False)
    product_id, = fieldvalues

    product = get_object_or_404(VoteProduct, id=product_id, active=True)
    activity = product.activity_id
    # 加入投票规则
    wechat_user_info = kwargs.get('wechat_user_info')
    openid = wechat_user_info.get('openid')
    if activity.is_endtime_active:
        if datetime.datetime.now() >= timezone.make_naive(activity.end_time):
            info['status'] = 1
            info['message'] = u'sorry,活动已截止'
            return JsonResponse(info, safe=False)
    if activity.vote_activity_max != 0:
        if VoteItem.objects.filter(activity_id_id=activity.id, vote_user_slug=openid).count() >= activity.vote_activity_max:
            info['status'] = 1
            info['message'] = u'您已达到投票上限'
            return JsonResponse(info, safe=False)
    if activity.vote_product_max != 0:
        if VoteItem.objects.filter(product_id_id=product.id, vote_user_slug=openid).count() >= activity.vote_product_max:
            info['status'] = 1
            info['message'] = u'您已达到投票上限'
            return JsonResponse(info, safe=False)
    if not activity.vote_self_enabled:
        if product.up_user_slug == openid:
            info['status'] = 1
            info['message'] = u'您不可以投票给自己'
            return JsonResponse(info, safe=False)

    # 正式投票
    try:
        with transaction.atomic(using='default', savepoint=True):
            wechat_fields = WeChatUser._meta.get_all_field_names()
            # wechat_user = WeChatUser(**dict(filter(lambda x:x[0] in wechat_fields, wechat_user_info.items())))
            # wechat_user.save()
            wechat_user, is_created = WeChatUser.objects.get_or_create(openid=openid, defaults=dict(filter(lambda x:x[0] in wechat_fields, wechat_user_info.items())))
            VoteItem.objects.create(product_id_id=product.id, activity_id_id=activity.id, vote_user_slug=openid, wechatuser=wechat_user)
            product.vote_count = modelsF('vote_count') + 1
            product.save()
    except Exception, e:
        info['status'] = 1
        info['message'] = u'投票失败'
        return JsonResponse(info, safe=False)

    return JsonResponse(info, safe=False)





####################################
# 活动详情页 #
# URL: /vote/activity/index/1/
####################################
@require_wechat_authorization()
@require_wechat_config()
@require_http_methods(["GET"])
def tmp_activity_index(request, *args, **kwargs):
    activity_id = kwargs.get('activity_id')
    wechat_config = kwargs.get('wechat_config')
    activity = get_object_or_404(VoteActivity, id=activity_id, active=True)
    ctx = {'activity': activity}
    ctx.update(wechat_config)
    ctx.update({'linkurl':'%(host)s%(path)s' % {'host':request.get_host(),'path':request.path}})
    template_name = 'vote/vote_activity_index.html'
    return render_to_response(template_name, RequestContext(request, ctx))




####################################
# 投票上传页 #
# URL: /vote/product/createform/1/
####################################
@require_wechat_authorization()
@require_wechat_config()
@require_http_methods(["GET"])
def tmp_product_createfrom(request, *args, **kwargs):
    activity_id = kwargs.get('activity_id')
    wechat_config = kwargs.get('wechat_config')
    activity = get_object_or_404(VoteActivity, id=activity_id, active=True)
    ctx = {'activity': activity}
    ctx.update(wechat_config)
    ctx.update({'linkurl':'%(host)s%(path)s' % {'host':request.get_host(),'path':request.path}})
    template_name = 'vote/vote_product_createform.html'
    return render_to_response(template_name, RequestContext(request, ctx))



####################################
# 单个投票product详情页 #
# URL: /vote/product/index/1/
####################################
@require_wechat_authorization()
@require_wechat_config()
@require_http_methods(["GET"])
def tmp_product_index(request, *args, **kwargs):
    product_id = kwargs.get('product_id')
    product = get_object_or_404(VoteProduct, id=product_id, active=True)
    wechat_user_info = kwargs.get('wechat_user_info')
    wechat_config = kwargs.get('wechat_config')
    openid = wechat_user_info.get('openid')
    ctx = {'product': product, 'is_self': (openid==product.up_user_slug)}
    ctx.update(wechat_config)
    ctx.update({'linkurl':'%(host)s%(path)s' % {'host':request.get_host(),'path':request.path}})
    template_name = 'vote/vote_product_index.html'
    return render_to_response(template_name, RequestContext(request, ctx))



####################################
# 投票排行榜页 #
# URL: /vote/products/list/1/
####################################
@require_wechat_authorization()
@require_wechat_config()
@require_http_methods(["GET"])
def tmp_products_list(request, *args, **kwargs):
    activity_id = kwargs.get('activity_id')
    wechat_config = kwargs.get('wechat_config')
    activity = get_object_or_404(VoteActivity, id=activity_id, active=True)
    ctx = {'activity': activity}
    template_name = 'vote/vote_products_list.html'
    ctx.update(wechat_config)
    ctx.update({'linkurl':'%(host)s%(path)s' % {'host':request.get_host(),'path':request.path}})
    return render_to_response(template_name, RequestContext(request, ctx))

