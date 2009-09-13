from django.conf.urls.defaults import patterns
from django import forms
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django_safeform import SafeForm, csrf_protect, csrf_utils, CsrfForm

class BasicForm(forms.Form):
    name = forms.CharField(max_length = 100)
SafeBasicForm = SafeForm(BasicForm)

class OtherForm(forms.Form):
    email = forms.EmailField()
SafeOtherForm = SafeForm(OtherForm)

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

@csrf_protect
def hand_rolled_view(request):
    if request.method == 'POST':
        csrf_token = request.POST.get('csrf_token', '')
        if not csrf_utils.validate_csrf_token(csrf_token, request):
            return HttpResponse('Invalid CSRF token')
        else:
            return HttpResponse('OK')
    else:
        return HttpResponse("""
        <form action="." method="post">
        <input type="text" name="name">
        <input type="hidden" name="csrf_token" value="%s">
        </form>
        """ % csrf_utils.new_csrf_token(request))

@csrf_protect
def two_forms_view(request):
    form1 = SafeBasicForm(request)
    form2 = SafeOtherForm(request)
    if form1.is_valid() and form2.is_valid():
        return HttpResponse(
            'Valid: %s, %s' % (
                form1.cleaned_data['name'], 
                form2.cleaned_data['email'],
            )
        )
    return HttpResponse("""
        <form action="." method="post">
        %s %s
        <p><input type="submit"></p>
        </form>
    """ % (form1.as_p(), form2.as_p()))

@csrf_protect
def safe_form_custom_message_view(request):
    form = SafeForm(BasicForm, invalid_message='Oh no!')(request)
    if form.is_valid():
        return HttpResponse('Valid')
    return HttpResponse(form.as_p())

@csrf_protect
def safe_form_ajax_skips_false_view(request):
    form = SafeForm(BasicForm, ajax_skips_check=False)(request)
    if form.is_valid():
        return HttpResponse('Valid')
    return HttpResponse(form.as_p())

class PersonForm(forms.Form):
    name = forms.CharField(max_length = 100)
    email = forms.EmailField()

PersonFormSet = formset_factory(PersonForm, extra=3)

@csrf_protect
def safe_formset_view(request):
    csrf_form = CsrfForm(request)
    formset = PersonFormSet()
    if request.method == 'POST':
        formset = PersonFormSet(request.POST)
        if csrf_form.is_valid() and formset.is_valid():
            return HttpResponse('Valid: %s' % ', '.join([
                '%(name)s [%(email)s]' % form.cleaned_data 
                for form in formset.forms
                if form.cleaned_data
            ]))
    return HttpResponse("""
        <form action="." method="post">
        %s %s %s
        <p><input type="submit"></p>
        </form>
    """ % (
        csrf_form,
        ''.join([f.as_p() for f in formset.forms]),
        formset.management_form
    ))

urlpatterns = patterns('',
    (r'^safe-basic-form/$', safe_form_view),
    (r'^two-forms/$', two_forms_view),
    (r'^safe-formset/$', safe_formset_view),
    (r'^safe-form-custom-message/$', safe_form_custom_message_view),
    (r'^safe-form-ajax-skips-false/$', safe_form_ajax_skips_false_view),    
    (r'^hand-rolled/$', hand_rolled_view),
)
