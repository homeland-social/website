from django.test import TestCase, Client
from django.urls import reverse


class AuthenticatedTestCase(TestCase):
    # Make sure a user exists in the database.
    fixtures = [
        'user.json',
    ]

    def setUp(self):
        # Obtain token and attach to test client.
        r = self.client.post(
            reverse('token_obtain_pair_view'),
            {
                'email': 'test@test.org',
                'password': 'password',
            },
        )
        token = r.json()['access']
        self.client = Client(HTTP_AUTHORIZATION=f'Bearer {token}')
