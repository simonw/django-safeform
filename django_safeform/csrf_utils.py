import time, datetime, hmac
from django.utils.hashcompat import sha_constructor as sha1
from django.conf import settings

def _csrf_token_from_request(request):
    if hasattr(request, '_csrf_token_to_set'):
        return request._csrf_token_to_set
    return request.COOKIES.get('_csrf_cookie', '')

def new_csrf_token(request, identifier='default'):
    epoch_time = int(
        time.mktime(datetime.datetime.utcnow().timetuple())
    )
    message = '%s:%s' % (identifier, epoch_time)
    secret_key = settings.SECRET_KEY + _csrf_token_from_request(request)
    sig = hmac.new(secret_key, message, sha1).hexdigest()
    return '%s:%s' % (message, sig)

not_set = object()

def validate_csrf_token(token, request, identifier='default', 
        expire_after=not_set):
    if not ':' in token:
        return False
    message, signature = token.rsplit(':', 1)
    secret_key = settings.SECRET_KEY + _csrf_token_from_request(request)
    expected_sig = hmac.new(secret_key, message, sha1).hexdigest()
    if signature != expected_sig:
        return False
    
    # Check the expiry and identifier
    token_identifier, created_at = message.split(':', 1)
    if token_identifier != identifier:
        return False
    
    if expire_after is not_set:
        expire_after = getattr(settings, 'CSRF_TOKENS_EXPIRE_AFTER', None)
    
    if expire_after is not None:
        epoch_time = int(
            time.mktime(datetime.datetime.utcnow().timetuple())
        )
        if int(created_at) + expire_after < epoch_time:
            return False
    
    return True
