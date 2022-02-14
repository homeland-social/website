from django.urls import reverse

from api.tests import APITestCase, AuthenticatedTestCase


NAME = '5b1c73d3-42af-4332-a21d-facfd310c412'
KEY = "AAAAE2VjZHNhLXNoYTItbmlzdHAzODQAAAAIbmlzdHAzODQAAABhBLeSFbMl7U1COq4o0VgJ0kSTDi2YV7uz1ifQMmDK1JPpip9EjZGTlmD7GobVyUbV7yGy9kykcusgJF0ZtEB3Bq7IkxH1x0lIkBUudKhhAyyvuTuHh09l3szieT2hsR13pw=="
TYPE = 'ecdsa-sha2-nistp384'


class SSHKeyTestCase(AuthenticatedTestCase):
    def test_create(self):
        r = self.client.post(reverse('sshkey-list'), {
            'name': NAME,
            'key': KEY,
            'type': TYPE,
        })
        self.assertEqual(201, r.status_code)
        self.assertEqual(NAME, r.json().get('name'))
        self.assertEqual(KEY, r.json().get('key'))
        self.assertEqual(TYPE, r.json().get('type'))


class SSHKeyVerifyTestCase(APITestCase):
    fixtures = {
        'user.json',
        'sshkey.json',
    }

    def test_verify(self):
        r = self.client.post(reverse('sshkey-verify', kwargs={'name': NAME}), {
            'key': KEY,
            'type': TYPE,
        })
        self.assertEqual(200, r.status_code)
