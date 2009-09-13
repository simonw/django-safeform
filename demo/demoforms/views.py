from django import forms
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django_safeform import SafeForm, csrf_protect, csrf_utils, CsrfForm

class SimpleForm(forms.Form):
    name = forms.CharField(max_length = 100)
SafeSimpleForm = SafeForm(SimpleForm)

class OtherForm(forms.Form):
    email = forms.EmailField()

@csrf_protect
def index(request):
    form = SafeSimpleForm(request)
    if form.is_valid():
        return HttpResponse(
            'Valid form submitted: %s' % form.cleaned_data['name']
        )
    
    return HttpResponse("""
        <form action="." method="post">
        %s
        <p><input type="submit"></p>
        </form>
        Current cookie is: %s (<a href="/clear/">clear</a>)<br>
        (Cookie headers may have been sent with this response)
    """ % (
        form.as_p(),
        request.COOKIES.get('_csrf_cookie', 'NOT SET'),
    ))

@csrf_protect
def templated(request):
    form = SafeSimpleForm(request)
    if form.is_valid():
        return HttpResponse(
            'Valid form submitted: %s' % form.cleaned_data['name']
        )
    return render_to_response('form.html', {
        'form': form,
        'csrf_cookie': request.COOKIES.get('_csrf_cookie', 'NOT SET'),
    })


@csrf_protect
def hand_rolled(request):
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
def custom_message(request):
    form = SafeForm(SimpleForm, invalid_message='Oh no!')(request)
    if form.is_valid():
        return HttpResponse('Valid')
    return HttpResponse('<form action="." method="post">' + form.as_p())

@csrf_protect
def multiple_forms(request):
    csrf_form = CsrfForm(request)
    simple_form = SimpleForm()
    other_form = OtherForm()
    if request.method == 'POST':
        simple_form = SimpleForm(request.POST)
        other_form = OtherForm(request.POST)
        if csrf_form.is_valid() and \
            simple_form.is_valid() and other_form.is_valid():
            return HttpResponse('Valid: %s, %s' % (
                simple_form.cleaned_data['name'],
                other_form.cleaned_data['email'],
            ))
    
    return render_to_response('multiple_forms.html', {
        'csrf_form': csrf_form,
        'simple_form': simple_form,
        'other_form': other_form,
        'csrf_cookie': request.COOKIES.get('_csrf_cookie', 'NOT SET'),
    })

class PersonForm(forms.Form):
    name = forms.CharField(max_length = 100)
    email = forms.EmailField()

PersonFormSet = formset_factory(PersonForm, extra=3)

@csrf_protect
def formset(request):
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
    return render_to_response('formset.html', {
        'csrf_form': csrf_form,
        'formset': formset,
        'csrf_cookie': request.COOKIES.get('_csrf_cookie', 'NOT SET'),
    })

def clear(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('_csrf_cookie')
    return response
