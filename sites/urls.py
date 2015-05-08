import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', TemplateView.as_view(template_name='index.html'), name="home"),
    (r'^', include('kidbook.urls')),
    url(r'^w/manage/', include(admin.site.urls)),
    #url(r'^admin/', include(admin.site.urls)),
    #(r'^ckeditor/', include('ckeditor.urls')),
    
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
