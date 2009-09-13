"""
Things to test:

1. That a form can be wrapped in a SafeForm
2. Error if cookie not present
3. Error if cookie present but altered
4. Error if csrf form value is incorrect
5. Error if csrf form value is tampered with
6. Error if csrf form value is more than CSRF_TOKEN_EXPIRES old
7. That SafeForm works with ModelForms, FormSets and so on
8. That a cookie is set by the decorator
9. That hand-rolled forms can be neatly protected as well
10. Form identifiers can be used to tie CSRF tokens to an individual form
"""

from django.test import TestCase
from django_safeform import csrf_utils
from django_safeform import test_utils
from django_safeform.forms import CSRF_INVALID_MESSAGE
import datetime

class SafeBasicFormTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def test_cookie_is_set(self):
        response = self.client.get('/safe-basic-form/')
        self.assert_(response.cookies.has_key('_csrf_cookie'))
    
    def test_submission_with_correct_csrf_token_works(self):
        response = self.client.get('/safe-basic-form/')
        inputs = test_utils.extract_input_tags(response.content)
        self.assert_(inputs.has_key('csrf_token'))
        token = inputs['csrf_token']
        response2 = self.client.post('/safe-basic-form/', {
            'csrf_token': token,
            'name': 'Test',
        })
        self.assertEqual(response2.content, 'Valid: Test')
    
    def test_submission_with_bad_token_fails(self):
        response = self.client.post('/safe-basic-form/', {
            'csrf_token': 'bad-token',
            'name': 'Test',
        })
        self.assert_(CSRF_INVALID_MESSAGE in response.content)
    
    def test_invalid_message_argument_sets_custom_message(self):
        response = self.client.post('/safe-form-custom-message/', {
            'csrf_token': 'bad-token',
            'name': 'Test',
        })
        self.assert_('Oh no!' in response.content)
    
    def test_ajax_submission_skips_csrf_check(self):
        response = self.client.post('/safe-basic-form/', {
            'name': 'Test',
        }, HTTP_X_REQUESTED_WITH = 'XMLHttpRequest')
        self.assertEqual(response.content, 'Valid: Test')
    
    def test_ajax_submission_fails_check_if_ajax_skips_check_is_false(self):
        response = self.client.post('/safe-form-ajax-skips-false/', {
            'name': 'Test',
        }, HTTP_X_REQUESTED_WITH = 'XMLHttpRequest')
        self.assert_(CSRF_INVALID_MESSAGE in response.content)

class MultipleFormsTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def test_two_safe_forms_does_not_result_in_duplicate_element_ids(self):
        response = self.client.get('/two-forms/')
        input_attrs = test_utils.extract_input_tag_attrs(response.content)
        ids = [d['id'] for d in input_attrs if 'id' in d]
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate IDs in %s' % ids)

class CsrfFormTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def test_csrf_form_can_protect_formsets(self):
        response = self.client.get('/safe-formset/')
        hiddens = test_utils.extract_input_tags(response.content)
        self.assert_('csrf_token' in hiddens)
        
        data = dict(hiddens)
        data['form-0-name'] = 'Simon'
        data['form-0-email'] = 'simon@example.com'
        data['form-1-name'] = 'Bob'
        data['form-1-email'] = 'bob@example.com'
        response2 = self.client.post('/safe-formset/', data)
        self.assertEqual(response2.content,
            'Valid: Simon [simon@example.com], Bob [bob@example.com]'
        )
        
        data['csrf_token'] = 'invalid-token'
        response3 = self.client.post('/safe-formset/', data)
        self.assert_(CSRF_INVALID_MESSAGE in response3.content)

class HandRolledFormsTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def test_hand_rolled_forms_can_be_protected(self):
        response = self.client.get('/hand-rolled/')
        self.assert_(response.cookies.has_key('_csrf_cookie'))
        inputs = test_utils.extract_input_tags(response.content)
        self.assert_(inputs.has_key('csrf_token'))
        
        response2 = self.client.post('/hand-rolled/', {
            'csrf_token': 'bad',
            'name': 'Test',
        })
        self.assertEqual(response2.content, 'Invalid CSRF token')
        
        response3 = self.client.post('/hand-rolled/', {
            'csrf_token': inputs['csrf_token'],
            'name': 'Test',
        })
        self.assertEqual(response3.content, 'OK')

class IdentifierTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def test_identifier_creates_tokens_that_only_work_with_one_form(self):
        # Get form token from a regular form
        response = self.client.get('/safe-basic-form/')
        token = test_utils.extract_input_tags(response.content)['csrf_token']
        self.assert_(token.startswith('default:'))
        response = self.client.post('/identifier-form/', {
            'name': 'Test',
            'csrf_token': token,
        })
        self.assert_(CSRF_INVALID_MESSAGE in response.content)
        
        # Now use the correct token
        response = self.client.get('/identifier-form/')
        token = test_utils.extract_input_tags(response.content)['csrf_token']
        self.assert_(token.startswith('identifier-form:'))
        response = self.client.post('/identifier-form/', {
            'name': 'Test 2',
            'csrf_token': token,
        })
        self.assertEqual(response.content, 'Valid: Test 2')

class ExpireAfterTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def fetch_token(self, fake):
        @test_utils.fake_utcnow(fake)
        def inner():
            r = self.client.get('/safe-basic-form/')
            return test_utils.extract_input_tags(r.content)['csrf_token']
        return inner()
    
    def test_expires_after_argument_causes_token_to_expire(self):
        token = self.fetch_token(datetime.datetime(2009, 1, 1, 0, 0, 0))
        @test_utils.fake_utcnow(datetime.datetime(2009, 1, 1, 0, 0, 59))
        def submission_should_succeed():
            response = self.client.post('/expire-after-60-seconds/', {
                'name': 'Test',
                'csrf_token': token,
            })
            self.assertEqual(response.content, 'Valid: Test')
        submission_should_succeed()
        
        @test_utils.fake_utcnow(datetime.datetime(2009, 1, 1, 0, 1, 1))
        def submission_should_fail():
            response = self.client.post('/expire-after-60-seconds/', {
                'name': 'Test',
                'csrf_token': token,
            })
            self.assert_(CSRF_INVALID_MESSAGE in response.content)
        submission_should_fail()
    
    def test_expires_after_default_is_set_by_global_settings_py(self):
        token = self.fetch_token(datetime.datetime(2009, 1, 1, 0, 0, 0))
        # Test pretends to run 2 days later
        @test_utils.fake_utcnow(datetime.datetime(2009, 1, 3, 0, 0, 0))
        def inner():
            response = self.client.post('/safe-basic-form/', {
                'name': 'Test',
                'csrf_token': token,
            })
            self.assertEqual(response.content, 'Valid: Test')
            # Now monkey patch the settings
            from django.conf import settings
            settings.CSRF_TOKENS_EXPIRE_AFTER = 24 * 60 * 60
            response = self.client.post('/safe-basic-form/', {
                'name': 'Test',
                'csrf_token': token,
            })
            self.assert_(CSRF_INVALID_MESSAGE in response.content)
            settings.CSRF_TOKENS_EXPIRE_AFTER = None
        inner()
