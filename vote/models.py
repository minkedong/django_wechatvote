# -*- coding:utf-8 -*-
import datetime
import uuid
from django.db import models
from django.utils import timezone
from qiniustorage.backends import QiniuMediaStorage

__all__ = ['VoteImage', 'VoteActivity', 'VoteProduct', 'VoteItem', 'WeChatUser']


class AbstractDefaultColumn(models.Model):
    create_uid = models.IntegerField(default=0)
    write_uid = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)  # 使用auto_now_add
    write_date = models.DateTimeField(auto_now=True)  # 使用auto_now

    class Meta:
        abstract = True



def upload_qiniu_name(instance, filename):
    # 自定义七牛上传文件名
    return 'vote/%(datepath)s/%(filename)s' % {'datepath':datetime.datetime.today().strftime('%Y/%m/%d'), 'filename':unicode(uuid.uuid1())}


####################################
# 图片 #
####################################
class VoteImage(models.Model):
    image = models.ImageField(storage=QiniuMediaStorage(), upload_to=upload_qiniu_name, max_length=256, null=True)

    def __unicode__(self):
        return unicode(self.image.url)



####################################
# 微信用户信息 #
####################################
class WeChatUser(models.Model):
    openid = models.CharField(default='', max_length=32, primary_key=True) # 用户的唯一标识
    nickname = models.CharField(default='', max_length=32) # 用户昵称
    # 用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
    sex = models.CharField(default='0', max_length=1, choices=(('0', 'unknown'), ('1', 'man'),('2', 'female')))
    province = models.CharField(default='', max_length=16) #    用户个人资料填写的省份
    city = models.CharField(default='', max_length=16) #    普通用户个人资料填写的城市
    country = models.CharField(default='', max_length=16) # 国家，如中国为CN
    # 用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
    headimgurl = models.CharField(default='', max_length=256)


####################################
# 投票活动 #
####################################
class VoteActivity(AbstractDefaultColumn):
    # 活动名
    name = models.CharField(default='', max_length=32)
    # 背景图（不同的投票活动可能只有背景图和活动详情图不一样，其他流程都一样）
    background_image = models.ForeignKey('VoteImage', related_name='activity_bg_image', blank=True, null=True, on_delete=models.SET_NULL)
    # 活动详情图
    detailinfo_image = models.ForeignKey('VoteImage', related_name='activity_di_image', blank=True, null=True, on_delete=models.SET_NULL)
    # 更多图片
    images = models.ManyToManyField('VoteImage', related_name='activity_images', blank=True)

    # 每个用户对一个活动最多可以上传几个作品（0表示无限制）
    up_product_max = models.PositiveIntegerField(default=0)
    # 每个用户对一个活动最多可以投几次票（0表示无限制）
    vote_activity_max = models.PositiveIntegerField(default=0)
    # 每个用户对一个作品最多可以投几次票（0表示无限制）
    vote_product_max = models.PositiveIntegerField(default=0)
    # 是否可以给自己投票
    vote_self_enabled = models.BooleanField(default=False)
    # 活动截止时间
    end_time = models.DateTimeField(default=timezone.now)
    # 是否验证活动截止时间
    is_endtime_active = models.BooleanField(default=False)

    # 是否可用
    active = models.BooleanField(default=True)

    # 获取活动页面地址
    def get_url(self):
        pass

    def __unicode__(self):
        return unicode(self.name)


####################################
# 投票上传 #
####################################
class VoteProduct(AbstractDefaultColumn):
    # 活动id
    activity_id = models.ForeignKey('VoteActivity', related_name='product_activity', blank=True, null=True, on_delete=models.SET_NULL)
    # 活动名
    activity_name = models.CharField(default='', max_length=32)
    # 上传图片
    images = models.ManyToManyField('VoteImage', related_name='product_images')
    # 上传的标题
    title = models.CharField(default='', max_length=32)
    # 上传的文字内容或备注
    content = models.CharField(default='', max_length=128)
    # 票数
    vote_count = models.PositiveIntegerField(default=0)
    # 上传用户的相关信息
    up_user_slug = models.CharField(default='', max_length=32) # 作为标志唯一用户
    up_user_name = models.CharField(default='', max_length=32)
    up_user_mobile = models.CharField(default='', max_length=11)
    up_user_email = models.EmailField(default='')
    wechatuser = models.ForeignKey('WeChatUser', related_name='product_wechatuser', blank=True, null=True, on_delete=models.SET_NULL)

    # 是否可用
    active = models.BooleanField(default=True)

    @property
    def image_first(self):
        return self.images.first()

    @property
    def image_first_url(self):
        image = self.images.first()
        return (image.image.url if image else '')

    @property
    def slug(self):
        return '%04d' % self.id

    


    class Meta:
        ordering = ['-id'] # 默认排序

    def __unicode__(self):
        return unicode('%(activity_name)s %(product_title)s' % {'activity_name':self.activity_name, 'product_title':self.title})



####################################
# 投票记录 #
####################################
class VoteItem(AbstractDefaultColumn):
    # 投票对象id
    product_id = models.ForeignKey('VoteProduct', related_name='item_activity', blank=True, null=True, on_delete=models.SET_NULL)
    # 投票活动id（冗余，方便后面统计使用）
    activity_id = models.ForeignKey('VoteActivity', related_name='item_activity', blank=True, null=True, on_delete=models.SET_NULL)
    # 备注
    note = models.CharField(default='', max_length=32)
    # 投票用户相关信息
    vote_user_slug = models.CharField(default='', max_length=32) # 作为标志唯一用户
    vote_user_name = models.CharField(default='', max_length=32)
    vote_user_mobile = models.CharField(default='', max_length=11)
    vote_user_email = models.EmailField(default='')
    wechatuser = models.ForeignKey('WeChatUser', related_name='item_wechatuser', blank=True, null=True, on_delete=models.SET_NULL)
