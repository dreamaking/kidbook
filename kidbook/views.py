# -*- coding: utf-8 -*-
import logging

import re
import urllib
import urllib2
import hashlib
import string
import traceback
import json
import time
import math
import subprocess
# Create your views here.
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms.models import model_to_dict
from django.db.models import Count
from models import *
from forms import *
from sites.settings import *

from django.core.cache import cache
# app specific files


LOG = logging.getLogger('django')


WEIXIN_TOKEN = 'kidbook'

WEIXIN_GLOBAL_URL_GET_TOKEN = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=%s&appid=%s&secret=%s'
WEIXIN_JSAPI_URL_GET_TICKET = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
WEIXIN_CARD_URL_GET_TICKET = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=wx_card'

WEIXIN_AUTH_URL_GET_CODE = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect'
WEIXIN_AUTH_URL_GET_TOKEN = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'

WEIXIN_AUTH_URL_GET_USERINFO = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN'


WEIXIN_APP_ID = 'wxf9dc3c84d5f267f2'
WEIXIN_APP_SECRET = '2d7162dabb71b045153fca2a06f9eddc'
WEIXIN_AUTH_SCOPE_1 = 'snsapi_base'
WEIXIN_AUTH_SCOPE_2 = 'snsapi_userinfo'
WEXIN_GLOBAL_TYPE = 'client_credential'


ACTIVITY_TICKET_SUPPORTER_NUM = 1


class api(object):
    def __init__(self, need_login=False):
        self.need_login = need_login

    def __call__(self, func):
        def _(request):
            try:
                if self.need_login and not request.user.id:
                    json_obj = {'error': 'auth'}
                else:
                    json_obj = func(request) or {}
                return HttpResponse(json.dumps(json_obj))
            except Exception as e:
                traceback.print_exc()
                return HttpResponse(json.dumps({'error': str(e)}))

        return _

def to_dict(**kwargs):
    temp = {}
    for key in kwargs.keys():
        value = kwargs.get(key)[0]
        if value != '':
            temp[key] = value
    return temp

       
def weixin_signature(request):
    token = WEIXIN_TOKEN
    params = request.GET
    args = [token, params['timestamp'], params['nonce']]
    args.sort()
    if hashlib.sha1("".join(args)).hexdigest() == params['signature']:
        if params.has_key('echostr'):
            return HttpResponse(params['echostr'])
        else:
            return HttpResponse("Invalid Request..")
    else:
        return HttpResponse("Invalid Request.")


def weixin_jsapi_signature(request):
    result = {}
    if cache.has_key('jsapi_ticket'):
        jsapi_ticket = cache.get('jsapi_ticket')
    else:
        access_token = weixin_access_token()
        ticket_object = weixin_get_jsapi_ticket(access_token['access_token'])
        jsapi_ticket = ticket_object['ticket']
        cache.set('jsapi_ticket', jsapi_ticket, 7000)

    params = request.GET
    s = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (jsapi_ticket, params['noncestr'], params['timestamp'], params['url'])
    signature = hashlib.sha1(s).hexdigest()
    print signature, jsapi_ticket, params['noncestr'], params['timestamp'], params['url']
    result['code'] = 200
    result['signature'] = signature
    result['ticket'] = jsapi_ticket
    return HttpResponse(json.dumps(result))

def weixin_card_signature(request):
    result = {}
    if cache.has_key('card_ticket'):
        card_ticket = cache.get('card_ticket')
    else:
        access_token = weixin_access_token()
        ticket_object = weixin_get_card_ticket(access_token['access_token'])
        card_ticket = ticket_object['ticket']
        cache.set('card_ticket', card_ticket, 7000)

    params = request.GET
    #array = [ params['timestamp'], params['openid'], params['code'], params['card_id'], params['balance'], card_ticket ]
    array = [ params['timestamp'], params['openid'], params['card_id'], params['balance'], card_ticket ]
    array.sort()
    s = ''.join(array)
    signature = hashlib.sha1(s).hexdigest()
    result['code'] = 200
    result['signature'] = signature
    result['ticket'] = card_ticket
    print "++++++++++++++", params['timestamp'], params['openid'], '''params['code']''', params['card_id'], params['balance'], card_ticket, signature
    return HttpResponse(json.dumps(result))

def set_test_list(request):
    access_token = weixin_access_token()['access_token'] 
    data = {'openid':['ofdNttzlQVptjchPScr9CqIwLqvw', 'ofdNtt3LNSh7KXDGJqXnpOHXNq24', 'ofdNtt5-WiHH451-YdmmuM_yqmiE', 'ofdNttyv1ARHgDKDEV-McGl5WCqc']}
    test_url = 'https://api.weixin.qq.com/card/testwhitelist/set?access_token=%s' % (access_token)
    result = urllib2.urlopen(url = test_url, data=json.dumps(data))  
    html = result.read()
    print '------------', html
    object = json.loads(html)
    return HttpResponse(json.dumps(object))

def weixin_get_jsapi_ticket(access_token):
    ticket_url = WEIXIN_JSAPI_URL_GET_TICKET % (access_token)
    ticket_object = fetch_object(ticket_url)
    return ticket_object

def weixin_get_card_ticket(access_token):
    ticket_url = WEIXIN_CARD_URL_GET_TICKET % (access_token)
    ticket_object = fetch_object(ticket_url)
    return ticket_object

def weixin_access_token():
    token_url = WEIXIN_GLOBAL_URL_GET_TOKEN % (WEXIN_GLOBAL_TYPE, WEIXIN_APP_ID, WEIXIN_APP_SECRET)
    token_object = fetch_object(token_url)
    return token_object

def weixin_get_token(code):
    token_url = WEIXIN_AUTH_URL_GET_TOKEN % (WEIXIN_APP_ID, WEIXIN_APP_SECRET, code)
    token_object = fetch_object(token_url)
    return token_object

def weixin_get_userinfo(access_token, openid):
    user_url = WEIXIN_AUTH_URL_GET_USERINFO % (access_token, openid)
    user_object = fetch_object(user_url)
    return user_object


def weixin_callback(request, state=None):
    code = request.GET.get('code')
    state = request.GET.get('state')
    token_object = weixin_get_token(code)

    if token_object.has_key('openid'):
        openid = token_object['openid']
    #else:
    #    print "#############################"
    user_object = User.objects.filter(openid = openid)
    if not user_object:

        # save user
        access_token = token_object['access_token']

        user = weixin_get_userinfo(access_token, openid)
        user_object = User(openid = user['openid'], nickname = user['nickname'], sex = user['sex'], province = user['province'], city = user['city'], country = user['country'], headimgurl = user['headimgurl'], access_token = token_object['access_token'], refresh_token = token_object['refresh_token'], scope = token_object['scope'], expires_in = token_object['expires_in'])
        user_object.save()

    state_object = json.loads(state)
    url = urllib2.unquote(state_object['url']) #+ "&openid=" + str(openid)
    response = HttpResponseRedirect(url)
    response.set_cookie('visitor_openid', openid, 3600 * 24 * 365)
    return response

def fetch_object(url):
    result = urllib2.urlopen(url)
    if result:
        html = result.read()
        print '------------', html
        object = json.loads(html)
        return object
    else:
        return None

def weixin_auth(request, url):
    state = {}
    state['url'] = urllib2.quote(url, 'utf8')
    state_json = json.dumps(state)
    redirect_uri = urllib2.quote("http://www.dreamaking.net/weixin_callback", 'utf8')
    auth_url =  WEIXIN_AUTH_URL_GET_CODE % (WEIXIN_APP_ID, redirect_uri, WEIXIN_AUTH_SCOPE_2, state_json)
    return HttpResponseRedirect(auth_url)


def upload_image(request):
    result = {}
    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        data = form.cleaned_data['image']
        openid = request.COOKIES.get('visitor_openid')
        user = User.objects.get(openid = openid)
        image = Image(image = data, user = user)
        image.save()
        oldpath = '/media/{0}'.format(image.image)
        newpath = get_thumbnail(image.image)
        command = ['convert', '-resize', '500x500', '/data/kidbook' + oldpath, '/data/kidbook' + newpath]
        subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True).wait()
        subprocess.call(command)
        result['code'] = 200
        result['imageid'] = image.id
        result['image'] = newpath
        return HttpResponse(json.dumps(result))
    else:
        result['code'] = 500
        return HttpResponse(json.dumps(result))
    

def save_image(request):
    result = {}
    imageid = request.POST.get('imageid')
    author = request.POST.get('author')
    phone = request.POST.get('phone')
    image_object = Image.objects.get(id = int(imageid))
    user = image_object.user
    user.author = author
    user.phone = phone
    user.save()
    
    response = HttpResponseRedirect('http://www.dreamaking.net/image/author/' + user.openid) 
    return response

def author_image(request, authorid):
    result = {}
    user = User.objects.get(openid = authorid)
    images = Image.objects.filter(user = user).order_by('-id')    
    result['images'] = images
   
    template = 'my.html' 
    return common_auth(request, template, result)

def all_image(request):
    result = {}
    template = 'list.html'
    return common_auth(request, template, result)
 
def gather_image(request):
    result = {}
    template = 'gather.html'
    return common_auth(request, template, result)

def query_image(request):
    result = {}
    pageno = request.GET.get('pageno')
    pagesize = request.GET.get('pagesize') 
    start = (int(pageno) - 1) * int(pagesize)
    images = Image.objects.all().order_by('-id')[start : start + int(pagesize)]
    result['code'] = 200
    data = []
    
    openid = request.COOKIES.get('visitor_openid')
    user = User.objects.get(openid = openid)
    like_list = json.loads(user.like_list) if user.like_list else {}

    for image in images:
        image_dict = {}
        image_dict['author'] = image.user.author
        image_dict['image'] = get_thumbnail(image.image)
        image_dict['imageid'] = image.id
        image_dict['likenum'] = image.likenum
        image_dict['liked'] = False
        image_dict['headimgurl'] = image.user.headimgurl
 
        if like_list.has_key(str(image.id)):
            image_dict['liked'] = True
 
        data.append(image_dict)
    result['data'] = data
    result['pagesize'] = int(pagesize)
    result['pageno'] = int(pageno)
    result['totalpage'] = int(math.ceil(Image.objects.all().count() / int(pagesize)))
    print pageno, pagesize, result['totalpage']
    return HttpResponse(json.dumps(result))

def like_image(request):
    result = {}
    imageid = request.GET.get('imageid')
    image = Image.objects.get(id = int(imageid))
    image.likenum = F('likenum') + 1
    image.save()

    openid = request.COOKIES.get('visitor_openid')
    user = User.objects.get(openid = openid)
    like_list = json.loads(user.like_list) if user.like_list else {}
    like_list[imageid] = int(imageid)
    user.like_list = json.dumps(like_list)
    user.likenum = len(like_list)
    user.save()
    result['code'] = 200
    return HttpResponse(json.dumps(result))

def common_auth(request, template, result):
    #reurl = 'http://www.dreamaking.net/image/gather'
    reurl = 'http://www.dreamaking.net' +  request.get_full_path()
    #openid = 'ofdNttzlQVptjchPScr9CqIwLqvw' 
    #openid = 'ofdNtt3LNSh7KXDGJqXnpOHXNq24'
   
    openid = request.COOKIES.get('visitor_openid')
    #if openid == 'ofdNtt3LNSh7KXDGJqXnpOHXNq24':
    #    openid = None
    if not openid:
        return weixin_auth(request, reurl.encode('utf8'))
    else:
        user = User.objects.get(openid = openid)
        if template:
            result['user'] = user
            response = render_to_response(template, result, context_instance=RequestContext(request))
            response.set_cookie('visitor_openid', openid, 3600 * 24 * 7)
        else:
            
            response = HttpResponseRedirect(reurl)
            response.set_cookie('visitor_openid', openid, 3600 * 24 * 7)

        #response.set_cookie('hidden_author', user.author, 3600 * 24 * 7)
        #response.set_cookie('hidden_phone', user.phone, 3600 * 24 * 7)
        return response

def save_company(request, id=None):
    result = {}
    if request.method == 'POST':
        company = request.POST.get('company')
        phone = request.POST.get('phone')
        intro = request.POST.get('intro')
        #contact = request.POST.get('contact')
        obj = Company(id = id, company = company, phone = phone, intro = intro)
        obj.save()
        result['company'] = company
        response = render_to_response("detail.html", result, context_instance=RequestContext(request))
        #response.set_cookie('id', id, 3600 * 24 * 365)
        return response
    else:
        company = Company.objects.get(id = id)
        result['company'] = company.company
        result['phone'] = company.phone
        result['intro'] = company.intro
        response = render_to_response("share.html", result, context_instance=RequestContext(request))
        #response.set_cookie('id', id, 3600 * 24 * 365)
        return response

def get_company(request):
    id = request.GET.get('id')
    company = Company.objects.get(id = id)
    return HttpResponse(json.dumps(company))

def coop(request):
    result = {}
    result['id'] = int(time.time())
    response = render_to_response("coop.html", result, context_instance=RequestContext(request))
    return response

def get_thumbnail(image):
    oldpath = '/media/{0}'.format(image)
    prefix = oldpath[0:oldpath.index('.')]
    suffix = oldpath[oldpath.index('.'):]
    newpath = prefix + '_s' + suffix
    return newpath


def all_vote(request):
    result = {}
    template = 'rank.html'
    votes = Vote.objects.all()
    result['votes'] = votes
    return common_auth(request, template, result)    

def save_vote(request):
    result = {}
    openid = request.POST.get('openid')
    bookname = request.POST.get('bookname')
    sex = request.POST.get('sex')
    age = request.POST.get('age')
    reason = request.POST.get('reason')
    user = User.objects.get(openid = openid)
    vote = Vote(user = user, bookname = bookname, sex = int(sex), age = int(age), reason = reason)
    vote.save()
    result['vote'] = vote
    #response = render_to_response("coupon.html", result, context_instance=RequestContext(request))
    #return response
    return pie_vote(request)

def pie_vote(request):
    result = {}
    vote_groups = Vote.objects.values('bookname').annotate(s_amount = Count('bookname'))
    groups = []
    for vote in vote_groups:
        group = {}
        group['bookname'] = vote['bookname']
        group['count'] = vote['s_amount']
        groups.append(group)
    result['vote_groups'] = groups
    response = render_to_response("pie.html", result, context_instance=RequestContext(request))
    return response


def check_ticket_vote(request):
    result = {}
    id = request.GET.get('id')
    vote = Vote.objects.get(id = int(id))
    if vote.is_receive:
        result['status'] = 'HAVE_RECEIVED'
    elif not activity.is_receive:
        result['status'] = 'RECEIVEABLE'
    result['code'] = 200
    return HttpResponse(json.dumps(result))

def receive_ticket_vote(request):
    result = check_ticket_vote(request)
    if result.get('status') == 'RECEIVEABLE':
        vote = Vote.objects.get(id = int(id))
        vote.is_receive = True
        vote.save()
        result['status'] = 'SUCCESS'
    else:
        result['status'] = 'FAIL'
    result['code'] = 200
    return HttpResponse(json.dumps(result))

def launch_activity(request):
    result = {}
    template = 'summon.html'
    response = common_auth(request, template, result)
    return response

def create_activity(request):
    result = {}
    openid = request.COOKIES.get('visitor_openid')
    user = User.objects.get(openid = openid)
    activity = Activity.objects.filter(owner = user)
    if not activity:
        activity = Activity(owner = user)
        activity.save()
    else:
        activity = activity[0]
    url = 'http://www.dreamaking.net/activity/get?id=' + str(activity.id)
    response = HttpResponseRedirect(url) 
    return response


def get_activity(request):
    result = {}
    openid = request.COOKIES.get('visitor_openid')
    if not openid:
        template = ''
        return common_auth(request, template, result) 
    
    user = User.objects.get(openid = openid)
    id = request.GET.get('id') 
    activity = Activity.objects.get(id = int(id))
    group = ActivityDetail.objects.filter(activity = activity)
    result['activity'] = activity
    result['group'] = group
    result['total'] = len(group)
    result['remain'] = ACTIVITY_TICKET_SUPPORTER_NUM  - len(group)
    result['is_enought'] = True if len(group) - ACTIVITY_TICKET_SUPPORTER_NUM >= 0 else False
    result['user'] = user
     # 判断是否是本人
    if activity.owner.openid == user.openid:
        template = 'tiki.html'
        response = render_to_response(template, result, context_instance=RequestContext(request))   
        return response
    # 判断有没有投票
    follower = ActivityDetail.objects.filter(activity = activity ,follower = user)
    if not follower:
        template = 'envelope.html'
        response = render_to_response(template, result, context_instance=RequestContext(request))
        return response
    template = 'tiki.html'
    result['is_follower'] = True
    response = render_to_response(template, result, context_instance=RequestContext(request))
    return response 


def support_activity(request):
    result = {}
    id = request.GET.get('id')
    activity = Activity.objects.get(id = int(id))
    openid = request.COOKIES.get('visitor_openid')
    user = User.objects.get(openid = openid)
    support = ActivityDetail.objects.filter(activity = activity, follower = user)
    if not support:
        ad = ActivityDetail(activity = activity, follower = user)
        ad.save()
    url = 'http://www.dreamaking.net/activity/get?id=' + id
    response = HttpResponseRedirect(url)
    return response    


def check_ticket_activity(request):
    result = {}
    id = request.GET.get('id')
    activity = Activity.objects.get(id = int(id))
    support = ActivityDetail.objects.filter(activity = activity)
    if len(support) < ACTIVITY_TICKET_SUPPORTER_NUM :
        result['status'] = 'NOT_ENOUGH_SUPPORTERS'
    elif activity.is_receive:
        result['status'] = 'HAVE_RECEIVED'
    elif not activity.is_receive:
        result['status'] = 'RECEIVEABLE'
    result['code'] = 200
    return HttpResponse(json.dumps(result))

def receive_ticket_activity(request):
    print "########"
    result = check_ticket_activity(request)
    if result.get('status') == 'RECEIVEABLE':
        activity = Activity.objects.get(id = int(id))
        activity.is_receive = True
        activity.save()
        result['status'] = 'SUCCESS'
    else:
        result['status'] = 'FAIL'
    result['code'] = 200
    return HttpResponse(json.dumps(result))

def clear(request):
    return render_to_response("clear-cookie.html", {}, context_instance=RequestContext(request))
