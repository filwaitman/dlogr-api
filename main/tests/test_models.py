# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from datetime import datetime

from django.utils import timezone

from main.tests.base import TestCase, CustomerFactory, EventFactory


class CustomerTestCase(TestCase):
    def test_representation(self):
        user = CustomerFactory.create(name='Filipe Waitman')
        self.assertEquals('{}'.format(user), 'Filipe Waitman')

    def test_get_full_name(self):
        user = CustomerFactory.create(name='Filipe Waitman')
        self.assertEquals(user.get_full_name(), 'Filipe Waitman')

    def test_get_short_name(self):
        user = CustomerFactory.create(name='Filipe Waitman')
        self.assertEquals(user.get_short_name(), 'Filipe Waitman')


class EventTestCase(TestCase):
    def test_representation(self):
        now = timezone.make_aware(datetime.now())
        event = EventFactory.create(
            object_id='abcd-efgh',
            object_type='users.models.User',
            timestamp=now,
            message='User signed up'
        )
        self.assertEquals(
            '{}'.format(event),
            'users.models.User/abcd-efgh at {}: User signed up'.format(now.isoformat().replace('T', ' '))
        )
