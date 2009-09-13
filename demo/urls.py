from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'demoforms.views.index'),
    (r'^clear/$', 'demoforms.views.clear'),
    (r'^templated/$', 'demoforms.views.templated'),
    (r'^hand-rolled/$', 'demoforms.views.hand_rolled'),
)
