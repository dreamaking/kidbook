from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^clear', clear),
    (r'^weixin_signature', weixin_signature),
    (r'^weixin_jsapi_signature', weixin_jsapi_signature),
    (r'^weixin_card_signature', weixin_card_signature),
    (r'^weixin_auth', weixin_auth),
    (r'^weixin_callback', weixin_callback), 

    (r'^coop', coop),
    (r'^company/save/(\d+)', save_company),
    (r'^company/get', get_company),
    
    (r'^image/upload', upload_image),
    (r'^image/save', save_image),
    (r'^image/author/([\w-]+)', author_image),
    (r'^image/query', query_image),
    (r'^image/like', like_image),
    (r'^image/gather', gather_image),
    (r'^image/all', all_image),
 
    (r'^vote/all', all_vote),
    (r'^vote/save', save_vote),
    (r'^vote/pie', pie_vote),
    (r'^vote/check_ticket', check_ticket_vote),
    (r'^vote/receive_ticket', receive_ticket_vote),
 
    (r'^activity/launch', launch_activity),
    (r'^activity/create', create_activity),
    (r'^activity/get', get_activity),
    (r'^activity/support', support_activity),
    (r'^activity/check_ticket', check_ticket_activity),
    (r'^activity/receive_ticket', receive_ticket_activity),
    
    url(r'^$', TemplateView.as_view(template_name='first.html'), name="first"),
    url(r'^first.html', TemplateView.as_view(template_name='first.html'), name="first"),
    url(r'^todo.html', TemplateView.as_view(template_name='todo.html'), name="todo"),
    url(r'^call.html', TemplateView.as_view(template_name='call.html'), name="call"),
    url(r'^who.html', TemplateView.as_view(template_name='who.html'), name="who"),
    url(r'^accept.html', TemplateView.as_view(template_name='accept.html'), name="accept"),


    (r'^set_test_list', set_test_list),
)

urlpatterns += staticfiles_urlpatterns()
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
