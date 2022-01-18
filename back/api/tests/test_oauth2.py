from django.urls import reverse

from . import AuthenticatedTestCase


AUTHZ_RESPONSE = {
    'client': {
        'user': {
            'username': 'testuser',
        },
        'client_name': 'Foobar',
        "website_uri": "https://foobar.org/foo-bar-baz/",
        "description": "Lorem ipsum dolor sit amet. Ut galisum ipsa ut eius sequi sit vitae sint vel commodi quia a voluptatem ducimus et minima minus. Vel nulla eaque et quia quidem a similique dolores sit mollitia odio est modi maiores eum ratione sunt. Quo ratione minima ab modi voluptatem et vitae tempora quo ipsum molestiae est adipisci nesciunt eum odit laborum. Quo iusto perferendis ut quos aliquam qui molestiae aperiam.",
        'scope': [
            'read-only',
        ],
    },
}


class OAuth2TestCase(AuthenticatedTestCase):
    fixtures = AuthenticatedTestCase.fixtures + [
        'oauth2client.json',
    ]

    def test_authorize(self):
        params = {
            'response_type': 'code',
            'client_id': 'foobar',
        }
        r = self.client.get(reverse('oauth_authorize_view'), params, secure=True)
        self.assertEqual(AUTHZ_RESPONSE, r.json())
