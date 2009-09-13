from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django_safeform.forms import SafeForm
from django_safeform.decorators import csrf_protect
from django_safeform import csrf_utils

class SimpleForm(forms.Form):
    name = forms.CharField(max_length = 100)
SafeSimpleForm = SafeForm(SimpleForm)

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

def clear(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('_csrf_cookie')
    return response

class Request:
    def __init__(self, post = None, cookies = None):
        self.COOKIES = cookies or {}
        self.POST = post or {}
        self.method = self.POST and 'POST' or 'GET'
