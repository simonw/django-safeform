from django.conf.urls.defaults import patterns
from django_safeform import csrf_utils
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django_safeform.forms import SafeForm
from django_safeform.decorators import csrf_protect

class BasicForm(forms.Form):
    name = forms.CharField(max_length = 100)
SafeBasicForm = SafeForm(BasicForm)

@csrf_protect
def safe_form_view(request):
    form = SafeBasicForm(request)
    if form.is_valid():
        return HttpResponse(
            'Valid: %s' % form.cleaned_data['name']
        )
    return HttpResponse("""
        <form action="." method="post">
        %s
        <p><input type="submit"></p>
        </form>
    """ % form.as_p())

def hand_rolled(request):
    if request.method == 'POST':
        pass # TODO: Finish this

urlpatterns = patterns('',
    (r'^safe-basic-form/$', safe_form_view),
    (r'^hand-rolled/$', hand_rolled),
)
