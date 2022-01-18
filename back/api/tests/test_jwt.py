from django.test import TestCase
from django.urls import reverse


class JWTTestCase(TestCase):
    # Make sure a user exists in the database.
    fixtures = [
        'user.json',
    ]

    def test_login_success(self):
        # Obtain token and attach to test client.
        r = self.client.post(
            reverse('token_obtain_pair_view'),
            {
                'email': 'test@test.org',
                'password': 'password',
            },
        )
        self.assertGreater(len(r.json()['access']), 1)
