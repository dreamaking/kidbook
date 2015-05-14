# -*- coding: utf-8 -*-
import re
import datetime
from django.db import models
from django.db.models import F
from model_utils.managers import PassThroughManager
from ckeditor.fields import RichTextField

from django.core.cache import cache

class User(models.Model):
    #userid = models.AutoField(primary_key=True)
    openid = models.CharField(u'微信用户ID', max_length=100, primary_key=True)
    headimgurl = models.URLField(u'用户头像')
    nickname = models.CharField(u'用户昵称', max_length=100)
    sex = models.IntegerField(u'用户性别')
    country = models.CharField(u'所在国家', max_length=100)
    province = models.CharField(u'所在省份', max_length=100)
    city = models.CharField(u'所在城市', max_length=100)
    privilege = models.CharField(u'微信用户特权', max_length=200)

    phone = models.CharField(u'手机', max_length=100)
    author = models.CharField(u'笔名', max_length=100)
    like_list = models.CharField(u'喜欢列表', max_length=2000)
    likenum =  models.IntegerField(u'点赞数', default=0)

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    modify_time = models.DateTimeField(u'修改时间', auto_now=True)

    scope = models.CharField(u'微信作用域', max_length=100)
    access_token = models.CharField(u'微信访问码', max_length=200)
    refresh_token = models.CharField(u'微信刷新码', max_length=200)
    expires_in = models.IntegerField(u'失效时间')
    unionid = models.CharField(u'UnionID', max_length=100)
    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户列表'

class Image(models.Model):
    id = models.AutoField(primary_key=True)

    image = models.FileField(upload_to = 'image/%Y-%m-%d')
    likenum = models.IntegerField(u'点赞数', default=0)
    is_active = models.BooleanField(u'是否可用', default=True)
    create_time = models.DateField(u'创建时间',auto_now_add=True)
    modify_time = models.DateField(u'修改时间',auto_now=True)
    user = models.ForeignKey( User)

    def image_display(self):
        url = self.get_thumbnail(self.image)
        return '<a href="{0}"><img src="{0}" style="width:100px"></a>'.format(url, url)
    image_display.allow_tags = True

    def edit(self):
        return '<a href="/w/manage/kidbook/image/{0}/">编辑</a>'.format(self.id)
    edit.allow_tags = True

    def get_author(self):
        return self.user.author
    
    def get_phone(self):
        return self.user.phone

    def get_thumbnail(self, image):
        oldpath = '/media/{0}'.format(image)
        prefix = oldpath[0:oldpath.index('.')]
        suffix = oldpath[oldpath.index('.'):]
        newpath = prefix + '_s' + suffix
        return newpath

    class Meta:
        verbose_name = u'图片'
        verbose_name_plural = u'图片列表'


class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    bookname = models.CharField(u'绘本名称', max_length=100)
    reason = models.CharField(u'推荐理由', max_length=1000)
    sex = models.IntegerField(u'性别')
    age = models.IntegerField(u'年龄')
    votenum = models.IntegerField(u'投票数', default=1)
    is_receive = models.BooleanField(u'是否领取', default=False)    
    is_active = models.BooleanField(u'是否可用', default=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    modify_time = models.DateTimeField(u'修改时间',auto_now=True)
    user = models.ForeignKey( User)


class Activity(models.Model):
    id = models.AutoField(primary_key=True)

    is_active = models.BooleanField(u'是否可用', default=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    modify_time = models.DateTimeField(u'修改时间',auto_now=True)
    owner = models.ForeignKey( User)
    is_receive = models.BooleanField(u'是否领取', default=False)

class ActivityDetail(models.Model):
    id = models.AutoField(primary_key=True)

    is_active = models.BooleanField(u'是否可用', default=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    modify_time = models.DateTimeField(u'修改时间',auto_now=True)
    follower = models.ForeignKey( User)
    activity = models.ForeignKey( Activity)

class Company(models.Model):
    #id = models.AutoField(primary_key=True)
    id =  models.CharField(max_length=20, primary_key=True)
    company = models.CharField(u'公司名称', max_length=200)
    phone = models.CharField(u'联系方式', max_length=200)
    contact = models.CharField(u'联系人', max_length=200)
    intro = models.CharField(u'公司简介', max_length=200)    

    is_active = models.BooleanField(u'是否可用', default=True)
    create_time = models.DateField(u'创建时间', auto_now_add=True)
    modify_time = models.DateField(u'修改时间', auto_now=True)
    
    class Meta:
        verbose_name = u'图书参展商'
        verbose_name_plural = u'图书参展商'


class Card(models.Model):
    id = models.CharField(u'卡券ID', max_length=100, primary_key=True)
    card_type = models.CharField(u'卡券类型', max_length=100)
    title = models.CharField(u'卡券标题', max_length=100)
    sub_title = models.CharField(u'卡券副标题', max_length=100)
    color = models.CharField(u'卡券颜色', max_length=100, choices=((u'1', '浅绿'),(u'2', '深绿'),(u'3', '浅蓝'), ('4', '深蓝'), ('5', '浅紫'), ('6', '土黄'), ('7', '明黄'), ('8', '橘黄'), ('9', '橘红'), ('4', '深红')))
    date_begin =  models.CharField(u'开始时间', max_length=100, null=True, blank=True)
    date_end =  models.CharField(u'结束时间', max_length=100, null=True, blank=True)   

    is_active = models.BooleanField(u'是否显示', default=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    modify_time = models.DateTimeField(u'修改时间',auto_now=True)

    class Meta:
        verbose_name = u'卡券'
        verbose_name_plural = u'卡券列表'
