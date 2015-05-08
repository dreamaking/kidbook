# -*- coding: utf-8 -*-

from django.contrib import admin
from kidbook import models


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company','phone', 'intro')
    search_fields = ('company', 'phone')


admin.site.register(models.Company, CompanyAdmin)

