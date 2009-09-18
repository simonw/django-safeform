try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.
import datetime, re

from django.http import SimpleCookie
from django.test.client import Client, MULTIPART_CONTENT
from django.test.testcases import TestCase
from django_safeform import csrf_utils

class CsrfClient(Client):
    class _CookieRequest:
        def __init__(self, cookies):
            if not '_csrf_cookie' in cookies:
                cookies['_csrf_cookie'] = 'csrf-cookie'
            self.COOKIES = dict([
                (key, cookies[key].value) for key in cookies
            ])
    
    def post(self, path, data={}, content_type=MULTIPART_CONTENT,
        follow=False, csrf='default', **extra):
        "Requests a response from the server using POST, auto-includes CSRF "
        "token unless csrf=False or the _csrf_cookie has not yet been set."
        if csrf and content_type == MULTIPART_CONTENT \
                and not data.has_key('csrf_token'):
            data['csrf_token'] = csrf_utils.new_csrf_token(
                CsrfClient._CookieRequest(self.cookies), csrf
            )
        return super(CsrfClient, self).post(
            path, data, content_type=content_type, follow=follow, csrf=csrf,
            **extra
        )

class CsrfTestCase(TestCase):
    def setUp(self):
        self.client = CsrfClient()

# Simple functions for extracting input tags from HTML - when you're testing 
# CSRF protection you need to be able to pull out the
#     <input type="hidden" name="csrf_token" value="...">
# tags so you can POST a correct value.

input_re = re.compile('<input(.*?)>')
attrib_re = re.compile(r'(\w+)=(["\'])(.*?)(\2)')

def extract_input_tag_attrs(html):
    "Returns a list of HTML attribute dictionaries for all inputs found"
    input_tags = []
    for input in input_re.findall(html):
        pairs = []
        for bits in attrib_re.findall(input):
            pairs.append((bits[0], bits[2]))
        input_tags.append(dict(pairs))
    return input_tags

def extract_input_tags(html):
    "Returns a dictionary of name => value for all inputs found"
    tag_attrs = extract_input_tag_attrs(html)
    return dict([
        (d['name'], d.get('value', ''))
        for d in tag_attrs
        if d.has_key('name')
    ])

# Decorator for temporarily monkey-patching datetime.utcnow

def fake_utcnow(fake):
    def outer(fn):
        def inner(*args, **kwargs):
            class _Object: pass
            orig_datetime = datetime.datetime
            fake_datetime = _Object()
            fake_datetime.utcnow = lambda: fake
            datetime.datetime = fake_datetime
            try:
                ret_value = fn(*args, **kwargs)
            finally: # or exception raised by fn() will not revert monkeypatch
                datetime.datetime = orig_datetime
            return ret_value
        return wraps(fn)(inner)
    return outer
