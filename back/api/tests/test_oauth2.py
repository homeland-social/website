import base64
from urllib.parse import urlparse, parse_qs

from django.urls import reverse

from api.tests import AuthenticatedTestCase


CLIENT_ID = b'19bbc55f-0f6f-4fca-95bc-f86286db43da'
CLIENT_SECRET = b'50ec237f-20b0-4a47-8a25-b329f6d53beb'
AUTHZ_PARAMS = {
    'response_type': 'code',
    'client_id': '19bbc55f-0f6f-4fca-95bc-f86286db43da',
    'redirect_uri': 'http://localhost:5000/oauth/',
    'state': 'lmnopqrstuv',
}

AUTHZ_RESPONSE = {
    'client': {
        'user': {
            'uid': '0Q',
            'username': 'testuser',
        },
        'client_id': '19bbc55f-0f6f-4fca-95bc-f86286db43da', 
        'client_name': 'Foobar',
        "website_uri": "https://foobar.org/foo-bar-baz/",
        "description": "Lorem ipsum dolor sit amet. Ut galisum ipsa ut eius sequi sit vitae sint vel commodi quia a voluptatem ducimus et minima minus. Vel nulla eaque et quia quidem a similique dolores sit mollitia odio est modi maiores eum ratione sunt. Quo ratione minima ab modi voluptatem et vitae tempora quo ipsum molestiae est adipisci nesciunt eum odit laborum. Quo iusto perferendis ut quos aliquam qui molestiae aperiam.",
        'scope': [
            'read-only',
        ],
    },
}


def get_code_from_url(url):
    return parse_qs(urlparse(url).query)['code']


def make_basic_header(username, password):
    basic_auth = base64.b64encode(b'%b:%b' % (username, password))
    return 'Basic ' + basic_auth.decode('utf8')


class OAuth2TestCase(AuthenticatedTestCase):
    fixtures = AuthenticatedTestCase.fixtures + [
        'oauth2client.json',
    ]

    def test_authorize_get(self):
        r = self.client.get(reverse('oauth_authorize_view'), AUTHZ_PARAMS, secure=True)
        self.assertEqual(AUTHZ_RESPONSE, r.json())

    def test_authorize_post_deny(self):
        r = self.client.post(reverse('oauth_authorize_view'), AUTHZ_PARAMS, secure=True)
        self.assertEqual(302, r.status_code)
        self.assertIn('denied', r.headers['location'])

    def test_authorize_post_confirm(self):
        params = AUTHZ_PARAMS.copy()
        params['confirm'] = 'true'
        r = self.client.post(reverse('oauth_authorize_view'), params, secure=True)
        self.assertEqual(302, r.status_code)
        self.assertIn('code', r.headers['location'])

    def test_token_get(self):
        params = AUTHZ_PARAMS.copy()
        params['confirm'] = 'true'
        r = self.client.post(reverse('oauth_authorize_view'), params, secure=True)
        self.assertEqual(302, r.status_code)
        url = r.headers['location']
        self.assertIn('code', url)
        params = {
            'code': get_code_from_url(url),
            'grant_type': 'authorization_code',
            'redirect_uri': params['redirect_uri'],
        }
        self.client.logout()
        r = self.client.post(
            reverse('oauth_token_view'), params,
            HTTP_AUTHORIZATION=make_basic_header(CLIENT_ID, CLIENT_SECRET),
            secure=True)
        self.assertEqual(200, r.status_code)
        self.assertIn('access_token', r.json())
