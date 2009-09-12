from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'demoforms.views.index'),
    (r'^clear/$', 'demoforms.views.clear'),
)
