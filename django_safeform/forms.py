try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.conf import settings
from django import forms
from csrf_utils import new_csrf_token, validate_csrf_token

_ = lambda s: s

CSRF_INVALID_MESSAGE = _('Form session expired - please resubmit')

def SafeForm(form_class, csrf_identifier='default'):
    class InnerSafeForm(form_class):
        def __init__(self, request, *args, **kwds):
            self.request = request
            if request.method == 'POST':
                super(InnerSafeForm, self).__init__(
                    request.POST, *args, **kwds
                )
            else:
                initial_data = kwds.get('initial', {})
                initial_data['csrf_token'] = new_csrf_token(self.request)
                kwds['initial'] = initial_data
                super(InnerSafeForm, self).__init__(*args, **kwds)
            self.fields['csrf_token'] = forms.CharField(
                widget = forms.HiddenInput,
                required = False
            )
        
        def clean(self):
            cleaned_data = super(InnerSafeForm, self).clean()
            token = cleaned_data.get('csrf_token', '')
            if not token or not validate_csrf_token(token, self.request):
                # Our form is "in flight", and we want the user to be able to 
                # successfully resubmit it. This means we need to include a 
                # freshly generated CSRF token in the hidden form field for 
                # when the form is redisplayed with the validation error.
                self.data._mutable = True
                self.data['csrf_token'] = new_csrf_token(self.request)
                self.data._mutable = False
                raise forms.ValidationError(CSRF_INVALID_MESSAGE)
            return cleaned_data
    
    return wraps(form_class, updated=())(InnerSafeForm)