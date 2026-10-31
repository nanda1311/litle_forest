from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


VERIFY = 'google.oauth2.id_token.verify_oauth2_token'
CLIENT_ID = 'test-client.apps.googleusercontent.com'
HOSTS = ['litleforest.com', 'localhost', 'testserver']


def google_claims(**overrides):
    claims = {
        'email': 'Plant.Lover@gmail.com',
        'email_verified': True,
        'given_name': 'Plant',
        'family_name': 'Lover',
    }
    claims.update(overrides)
    return claims


@override_settings(GOOGLE_CLIENT_ID=CLIENT_ID, ALLOWED_HOSTS=HOSTS)
class GoogleLoginTests(TestCase):

    def start(self, host='litleforest.com'):
        res = self.client.get(reverse('google_login'), HTTP_HOST=host)
        self.assertEqual(res.status_code, 302)
        return parse_qs(urlparse(res['Location']).query), res['Location']

    def callback(self, state, claims=None, host='litleforest.com', nonce=None, **verify_kwargs):
        if claims is not None and 'nonce' not in claims:
            claims = dict(claims, nonce=nonce or self.client.session['google_oauth']['nonce'])
        with mock.patch(VERIFY, return_value=claims, **verify_kwargs) as verify:
            res = self.client.post(reverse('google_complete'),
                                   {'id_token': 'signed.jwt.token', 'state': state}, HTTP_HOST=host)
        return res, verify

    def assertLoggedInAs(self, user):
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def assertNotLoggedIn(self):
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_start_redirects_to_google_with_https_callback(self):
        params, location = self.start()
        self.assertTrue(location.startswith('https://accounts.google.com/o/oauth2/v2/auth?'))
        self.assertEqual(params['client_id'], [CLIENT_ID])
        self.assertEqual(params['redirect_uri'], ['https://litleforest.com/auth/google/callback/'])
        self.assertEqual(params['response_type'], ['id_token'])
        self.assertEqual(params['scope'], ['openid email profile'])
        self.assertEqual(params['state'], [self.client.session['google_oauth']['state']])

    def test_localhost_callback_uses_http(self):
        params, _ = self.start(host='localhost:8000')
        self.assertEqual(params['redirect_uri'], ['http://localhost:8000/auth/google/callback/'])

    def test_new_user_is_created_and_logged_in(self):
        params, _ = self.start()
        res, verify = self.callback(params['state'][0], google_claims())

        self.assertRedirects(res, reverse('home'), fetch_redirect_response=False)
        self.assertEqual(verify.call_args[0][0], 'signed.jwt.token')
        self.assertEqual(verify.call_args[0][2], CLIENT_ID)
        user = User.objects.get(email='plant.lover@gmail.com')
        self.assertEqual(user.first_name, 'Plant')
        self.assertFalse(user.has_usable_password())
        self.assertLoggedInAs(user)

    def test_existing_user_matched_by_email_case_insensitively(self):
        existing = User.objects.create_user('plantlover', 'plant.lover@GMAIL.com', 'pw-12345')
        params, _ = self.start()
        self.callback(params['state'][0], google_claims())

        self.assertEqual(User.objects.count(), 1)
        self.assertLoggedInAs(existing)
        existing.refresh_from_db()
        self.assertTrue(existing.check_password('pw-12345'))

    def test_username_collision_gets_suffix(self):
        User.objects.create_user('plant.lover', 'someone-else@example.com', 'pw')
        params, _ = self.start()
        self.callback(params['state'][0], google_claims())
        new_user = User.objects.get(email='plant.lover@gmail.com')
        self.assertNotEqual(new_user.username, 'plant.lover')
        self.assertTrue(new_user.username.startswith('plant.lover'))

    def test_state_mismatch_rejected(self):
        self.start()
        res, verify = self.callback('forged-state', google_claims(nonce='x'))
        self.assertRedirects(res, reverse('loginaccount'), fetch_redirect_response=False)
        verify.assert_not_called()
        self.assertNotLoggedIn()

    def test_callback_without_start_rejected(self):
        res, verify = self.callback('anything', google_claims(nonce='x'))
        self.assertRedirects(res, reverse('loginaccount'), fetch_redirect_response=False)
        verify.assert_not_called()
        self.assertNotLoggedIn()

    def test_state_cannot_be_replayed(self):
        params, _ = self.start()
        self.callback(params['state'][0], google_claims())
        self.client.logout()
        res, verify = self.callback(params['state'][0], google_claims(nonce='x'))
        verify.assert_not_called()
        self.assertNotLoggedIn()

    def test_nonce_mismatch_rejected(self):
        params, _ = self.start()
        res, _ = self.callback(params['state'][0], google_claims(nonce='attacker-nonce'))
        self.assertRedirects(res, reverse('loginaccount'), fetch_redirect_response=False)
        self.assertEqual(User.objects.count(), 0)
        self.assertNotLoggedIn()

    def test_invalid_id_token_rejected(self):
        params, _ = self.start()
        res, _ = self.callback(params['state'][0], side_effect=ValueError('bad signature'))
        self.assertRedirects(res, reverse('loginaccount'), fetch_redirect_response=False)
        self.assertNotLoggedIn()

    def test_callback_page_forwards_fragment_with_csrf(self):
        res = self.client.get(reverse('google_callback'), HTTP_HOST='litleforest.com')
        self.assertContains(res, f'action="{reverse("google_complete")}"')
        self.assertContains(res, 'csrfmiddlewaretoken')
        self.assertContains(res, 'window.location.hash')

    def test_complete_requires_csrf(self):
        client = self.client_class(enforce_csrf_checks=True)
        res = client.post(reverse('google_complete'), {'id_token': 't', 'state': 's'}, HTTP_HOST='litleforest.com')
        self.assertEqual(res.status_code, 403)

    def test_complete_rejects_get(self):
        res = self.client.get(reverse('google_complete'), HTTP_HOST='litleforest.com')
        self.assertEqual(res.status_code, 405)

    def test_unverified_email_rejected(self):
        params, _ = self.start()
        self.callback(params['state'][0], google_claims(email_verified=False))
        self.assertEqual(User.objects.count(), 0)
        self.assertNotLoggedIn()

    def test_inactive_user_rejected(self):
        User.objects.create_user('x', 'plant.lover@gmail.com', 'pw', is_active=False)
        params, _ = self.start()
        self.callback(params['state'][0], google_claims())
        self.assertNotLoggedIn()

    def test_user_cancelled_at_google(self):
        self.start()
        res = self.client.post(reverse('google_complete'), {'error': 'access_denied'}, HTTP_HOST='litleforest.com')
        self.assertRedirects(res, reverse('loginaccount'), fetch_redirect_response=False)
        self.assertNotLoggedIn()

    def test_login_and_signup_pages_show_google_button(self):
        for name, label in (('loginaccount', 'Continue with Google'), ('createaccount', 'Sign up with Google')):
            res = self.client.get(reverse(name), HTTP_HOST='litleforest.com')
            self.assertContains(res, f'href="{reverse("google_login")}"')
            self.assertContains(res, label)


@override_settings(GOOGLE_CLIENT_ID='', ALLOWED_HOSTS=HOSTS)
class GoogleLoginDisabledTests(TestCase):

    def test_button_hidden_and_start_refuses_without_client_id(self):
        res = self.client.get(reverse('loginaccount'), HTTP_HOST='litleforest.com')
        self.assertNotContains(res, 'google-signin-btn')
        res = self.client.get(reverse('google_login'), HTTP_HOST='litleforest.com')
        self.assertRedirects(res, reverse('loginaccount'), fetch_redirect_response=False)
