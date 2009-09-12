try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.utils.hashcompat import sha_constructor as sha1
from django.conf import settings
from django import forms
SECRET_KEY = settings.SECRET_KEY
import time, datetime, hmac

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
                initial_data['_csrf_token'] = self.csrf_token_for_form()
                kwds['initial'] = initial_data
                super(InnerSafeForm, self).__init__(*args, **kwds)
            self.fields['_csrf_token'] = forms.CharField(
                widget = forms.HiddenInput,
                required = False
            )
        
        def csrf_token_from_request(self):
            if hasattr(self.request, '_csrf_token_to_set'):
                return self.request._csrf_token_to_set
            return self.request.COOKIES.get('_csrf_cookie', '')
        
        def csrf_token_for_form(self):
            epoch_time = int(
                time.mktime(datetime.datetime.utcnow().utctimetuple())
            )
            message = '%s:%s' % (csrf_identifier, epoch_time)
            secret_key = SECRET_KEY + self.csrf_token_from_request()
            sig = hmac.new(secret_key, message, sha1).hexdigest()
            return '%s:%s' % (message, sig)
        
        def csrf_validate_token_signature(self, token):
            if not ':' in token:
                return False
            message, signature = token.rsplit(':', 1)
            secret_key = SECRET_KEY + self.csrf_token_from_request()
            expected_sig = hmac.new(secret_key, message, sha1).hexdigest()
            return signature == expected_sig
        
        def clean(self):
            cleaned_data = super(InnerSafeForm, self).clean()
            token = cleaned_data.get('_csrf_token', '')
            if not token or not self.csrf_validate_token_signature(token):
                # Our form is "in flight", and we want the user to be able to 
                # successfully resubmit it. This means we need to include a 
                # freshly generated CSRF token in the hidden form field for 
                # when the form is redisplayed with the validation error.
                self.data._mutable = True
                self.data['_csrf_token'] = self.csrf_token_for_form()
                self.data._mutable = False
                raise forms.ValidationError(CSRF_INVALID_MESSAGE)
            return cleaned_data
    
    return wraps(form_class, updated=())(InnerSafeForm)
