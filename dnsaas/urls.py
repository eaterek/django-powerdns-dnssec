from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from dnsaas.utils import VERSION
from powerdns.utils import patterns
from powerdns.views import obtain_auth_token
from ui.views import start_page


title = settings.SITE_TITLE
title_v = ' '.join([title, VERSION])

admin.site.site_title = title
admin.site.site_header = title_v
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('dnsaas.api.urls', namespace='api')),
    url(r'^api-token-auth/', obtain_auth_token, name='get-api-token'),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
    url(r'^$', start_page, name='home'),
)
