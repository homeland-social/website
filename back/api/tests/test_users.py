from django.urls import reverse
from django.test import TestCase

from api.tests import APITestCase, AuthenticatedTestCase
from api.models import User


class UsersTestCase(APITestCase):
    def test_create(self):
        r = self.client.post(reverse('user-list'), {
            'email': 'test@test.org',
            'username': 'username',
            'password': 'password',
            'recaptcha': 'foobar',
        })
        self.assertEqual(201, r.status_code)
        self.assertEqual('username', r.json().get('username'))
        self.assertEqual('test@test.org', r.json().get('email'))
        user = User.objects.get(username='username')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_confirmed)


class UserConfirmTestCase(APITestCase):
    fixtures = [
        'user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.confirmation = self.user.generate_confirmation()

    def test_confirm(self):
        self.assertTrue(
            self.user.validate_confirmation(
                ts=self.confirmation['ts'],
                signature=self.confirmation['signature'],
            )
        )

    def test_confirm_post(self):
        r = self.client.post(
            reverse('user-confirm', kwargs={'uid': self.user.uid}), {
            'ts': self.confirmation['ts'],
            'signature': self.confirmation['signature'].decode(),
        })
        self.assertEqual(302, r.status_code)


class UserLoginTestCase(APITestCase):
    fixtures = [
        'user.json',
    ]

    def test_login(self):
        r = self.client.post(reverse('user-login'), {
            'email': 'test@test.org',
            'password': 'password',
        })
        self.assertEqual(200, r.status_code)


class UserLoggedInTestCase(AuthenticatedTestCase):
    def test_logout(self):
        r = self.client.post(reverse('user-logout'))
        self.assertEqual(204, r.status_code)

    def test_whoami(self):
        r = self.client.get(reverse('user-whoami'))
        self.assertEqual(200, r.status_code)
        self.assertEqual('test@test.org', r.json().get('email'))
        self.assertEqual('testuser', r.json().get('username'))
