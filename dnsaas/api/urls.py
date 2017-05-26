from django.conf.urls import include, url

from powerdns.utils import patterns


urlpatterns = patterns(
    '',
    url(r'^v2/', include('dnsaas.api.v2.urls', namespace='v2')),
)
