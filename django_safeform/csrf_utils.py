import time, datetime, hmac
from django.utils.hashcompat import sha_constructor as sha1
from django.conf import settings
SECRET_KEY = settings.SECRET_KEY

def _csrf_token_from_request(request):
    if hasattr(request, '_csrf_token_to_set'):
        return request._csrf_token_to_set
    return request.COOKIES.get('_csrf_cookie', '')

def new_csrf_token(request, csrf_identifier='default'):
    epoch_time = int(
        time.mktime(datetime.datetime.utcnow().utctimetuple())
    )
    message = '%s:%s' % (csrf_identifier, epoch_time)
    secret_key = SECRET_KEY + _csrf_token_from_request(request)
    sig = hmac.new(secret_key, message, sha1).hexdigest()
    return '%s:%s' % (message, sig)

def validate_csrf_token(token, request):
    if not ':' in token:
        return False
    message, signature = token.rsplit(':', 1)
    secret_key = SECRET_KEY + _csrf_token_from_request(request)
    expected_sig = hmac.new(secret_key, message, sha1).hexdigest()
    return signature == expected_sig
