from django.test import TestCase, Client
from django.urls import reverse

from rest_framework.test import APIClient


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()


class AuthenticatedTestCase(APITestCase):
    # Make sure a user exists in the database.
    fixtures = [
        'user.json',
    ]

    def setUp(self):
        self.client.login(email='test@test.org', password='password')
