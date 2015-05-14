# -*- coding: utf-8 -*-

from django.contrib import admin
from kidbook import models


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company','phone', 'intro')
    search_fields = ('company', 'phone')


class CardAdmin(admin.ModelAdmin):
    list_display = ('id','card_type', 'title', 'sub_title', 'color', 'date_begin', 'date_end',)
    search_fields = ('title',)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_display', 'likenum', 'get_author','get_phone', 'is_active', 'edit')
    readonly_fields =  ('image_display', 'likenum', 'get_author','get_phone')
    fields = ('image_display', 'likenum', 'get_author','get_phone', 'is_active',)

    def get_readonly_fields(self,request,obj=None):
        return self.readonly_fields 
 
admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Card, CardAdmin)
admin.site.register(models.Image, ImageAdmin)

