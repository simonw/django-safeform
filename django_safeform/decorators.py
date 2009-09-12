from django.utils.hashcompat import sha_constructor as sha1
import random
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

def csrf_protect(view_func):
    def inner(request, *args, **kwargs):
        need_to_set_the_cookie = False
        csrf_token = request.COOKIES.get('_csrf_cookie')
        if not csrf_token:
            need_to_set_the_cookie = True
            csrf_token = sha1(str(random.random())).hexdigest()
            request._csrf_token_to_set = csrf_token
        response = view_func(request, *args, **kwargs)
        if need_to_set_the_cookie:
            response.set_cookie('_csrf_cookie', csrf_token)
        return response
    return wraps(view_func)(inner)
