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
            'csrf_token': 'bad-taken',
            'name': 'Test',
        })
        self.assert_(CSRF_INVALID_MESSAGE in response.content)

class MultipleFormsTest(TestCase):
    urls = 'django_safeform.test_views'
    
    def test_two_forms_does_not_result_in_duplicate_element_ids(self):
        response = self.client.get('/two-forms/')
        input_attrs = test_utils.extract_input_tag_attrs(response.content)
        ids = [d['id'] for d in input_attrs if 'id' in d]
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate IDs in %s' % ids)

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
