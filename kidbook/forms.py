# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from django import forms
from models import *

class ImageForm(forms.Form):
    #openid = forms.CharField()
    image = forms.FileField()
