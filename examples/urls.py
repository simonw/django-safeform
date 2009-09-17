from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'demoforms.views.index'),
    (r'^clear/$', 'demoforms.views.clear'),
    (r'^templated/$', 'demoforms.views.templated'),
    (r'^get-form/$', 'demoforms.views.get_form'),
    (r'^hand-rolled/$', 'demoforms.views.hand_rolled'),
    (r'^custom-message/$', 'demoforms.views.custom_message'),
    (r'^multiple-forms/$', 'demoforms.views.multiple_forms'),
    (r'^formset/$', 'demoforms.views.formset'),
)
