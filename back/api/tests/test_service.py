from django.test import TestCase

from api.models import Service, ServiceVersion


class ServiceTestCase(TestCase):
    def test_create_service(self):
        service = Service.objects.create(
            name='test_service',
            group='tools',
            description='A service for testing',
        )
        service_version = ServiceVersion.objects.create(
            service=service,
            version='1.0',
        )
        self.assertEqual(1, service.versions.all().count())
