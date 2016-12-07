# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from datetime import datetime
import uuid

import factory
from faker import Faker
from rest_framework.test import APIClient, APITestCase as DRFAPITestCase

from django.test import TestCase as DjangoTestCase
from django.utils import timezone

from main.models import Customer, Event

fake = Faker()
TEST_USER_PASSWORD_TEXT = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
        strategy = factory.CREATE_STRATEGY

    name = factory.lazy_attribute(lambda x: fake.name())
    email = factory.Sequence(lambda x: '{}@example.com'.format(uuid.uuid4()))
    password = factory.PostGenerationMethodCall('set_password', TEST_USER_PASSWORD_TEXT)
    timezone = 'UTC'


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event
        strategy = factory.CREATE_STRATEGY

    customer = factory.SubFactory(CustomerFactory)
    object_id = factory.lazy_attribute(lambda x: uuid.uuid4())
    object_type = factory.lazy_attribute(lambda x: '{}.{}.{}'.format(fake.word(), fake.word(), fake.word()))
    human_identifier = factory.lazy_attribute(lambda x: fake.name())
    timestamp = factory.lazy_attribute(lambda x: timezone.make_aware(datetime.now()))
    message = factory.lazy_attribute(lambda x: fake.sentence())


class BaseTestMixin(object):
    pass


class TestCase(BaseTestMixin, DjangoTestCase):
    pass


class APITestCase(BaseTestMixin, DRFAPITestCase):
    def setUp(self):
        super(APITestCase, self).setUp()

        self.user_password = 'supersikret'
        self.user = CustomerFactory.create(email='test@example.com')
        self.user.set_password(self.user_password)
        self.user.save()

        self.authorization = 'Token {}'.format(self.user.auth_token.key)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=self.authorization)
