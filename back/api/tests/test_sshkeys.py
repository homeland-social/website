from django.urls import reverse

from api.tests import APITestCase, AuthenticatedTestCase


UUID = '0ac99280-5233-47d1-a43b-b02379e832d0'
KEY = "AAAAE2VjZHNhLXNoYTItbmlzdHAzODQAAAAIbmlzdHAzODQAAABhBLeSFbMl7U1COq4o0VgJ0kSTDi2YV7uz1ifQMmDK1JPpip9EjZGTlmD7GobVyUbV7yGy9kykcusgJF0ZtEB3Bq7IkxH1x0lIkBUudKhhAyyvuTuHh09l3szieT2hsR13pw=="
TYPE = 'ecdsa-sha2-nistp384'


class SSHKeyTestCase(AuthenticatedTestCase):
    fixtures = {
        'user.json',
    }

    def test_register_missing(self):
        r = self.client.post(reverse('console-register'), {
            'uuid': UUID,
            'domain_name': 'foobar.com',
            'key': KEY,
            'type': TYPE,
        })
        self.assertEqual(201, r.status_code)
        self.assertEqual(UUID, r.json().get('uuid'))


class SSHKeyVerifyTestCase(APITestCase):
    fixtures = {
        'user.json',
        'console.json',
        'sshkey.json',
    }

    def test_verify(self):
        r = self.client.post(reverse('console-verify-key', kwargs={'uuid': UUID}), {
            'key': KEY,
            'type': TYPE,
        })
        self.assertEqual(200, r.status_code)
