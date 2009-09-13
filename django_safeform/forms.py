try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.conf import settings
from django import forms
from csrf_utils import new_csrf_token, validate_csrf_token

_ = lambda s: s

CSRF_INVALID_MESSAGE = _('Form session expired - please resubmit')

class HiddenInputNoId(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        if attrs and 'id' in attrs:
            del attrs['id']
        return super(HiddenInputNoId, self).render(name, value, attrs)

not_set = object()

def SafeForm(form_class,
        identifier='default',
        invalid_message=CSRF_INVALID_MESSAGE,
        ajax_skips_check=True,
        expire_after=not_set
    ):
    class InnerSafeForm(form_class):
        def __init__(self, request, *args, **kwds):
            self.request = request
            if request.method == 'POST':
                super(InnerSafeForm, self).__init__(
                    request.POST, *args, **kwds
                )
            else:
                initial_data = kwds.get('initial', {})
                initial_data['csrf_token'] = new_csrf_token(
                    self.request,
                    identifier=identifier,
                )
                kwds['initial'] = initial_data
                super(InnerSafeForm, self).__init__(*args, **kwds)
            self.fields['csrf_token'] = forms.CharField(
                widget = HiddenInputNoId,
                required = False,
            )
        
        def clean(self):
            cleaned_data = super(InnerSafeForm, self).clean()
            token = cleaned_data.get('csrf_token', '')
            kwargs = dict(identifier=identifier)
            if expire_after is not not_set:
                kwargs['expire_after'] = expire_after
            if not token or not validate_csrf_token(
                    token, self.request, **kwargs
                ):
                # Our form is "in flight", and we want the user to be able to 
                # successfully resubmit it. This means we need to include a 
                # freshly generated CSRF token in the hidden form field for 
                # when the form is redisplayed with the validation error.
                if not (ajax_skips_check and self.request.is_ajax()):
                    self.data._mutable = True
                    self.data['csrf_token'] = new_csrf_token(self.request)
                    self.data._mutable = False
                    raise forms.ValidationError(invalid_message)
            return cleaned_data
    
    return wraps(form_class, updated=())(InnerSafeForm)

class CsrfForm(forms.Form):
    def __unicode__(self):
        # Default rendering should output the error list or nothing at all
        return self.as_p()
CsrfForm = SafeForm(CsrfForm)
