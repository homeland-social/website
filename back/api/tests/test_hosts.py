from django.urls import reverse

from api.tests import AuthenticatedTestCase
from api.models import Hostname, User


class HostsTestCase(AuthenticatedTestCase):
    fixtures = [
        'user.json',
        'host.json',
    ]

    def test_create_duplicate(self):
        r = self.client.post(reverse('host-list'), {'name': 'google.com'})
        self.assertEqual(400, r.status_code)
        self.assertEqual(['hostname with this name already exists.'], r.json().get('name'))

    def test_shared(self):
        r = self.client.get(reverse('host-shared'))
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r.json(), list)

    def test_check(self):
        r = self.client.post(reverse('host-check'), {'name': 'google.com'})
        self.assertEqual(200, r.status_code)
        r = self.client.post(reverse('host-check'), {'name': 'foo.shanty.local'})
        self.assertEqual(404, r.status_code)

    def test_dig(self):
        r = self.client.post(reverse('host-dig', kwargs={'name': 'google.com'}))
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r.json().get('google.com'), list)

    def test_port_scan(self):
        r = self.client.post(reverse('host-port-scan'))
        self.assertEqual(200, r.status_code)
        self.assertIn(r.json().get('80'), ['closed', 'open'])
        self.assertIn(r.json().get('443'), ['closed', 'open'])
