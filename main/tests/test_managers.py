# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from main.models import Customer
from main.tests.base import TestCase


class CustomerManagerTestCase(TestCase):
    def test_manager_create_user(self):
        user = Customer.objects.create_user(
            email='filwaitman@gmail.com', password='supersikret42', name='Sloth', timezone='UTC'
        )
        self.assertEquals(user.email, 'filwaitman@gmail.com')
        self.assertEquals(user.name, 'Sloth')
        self.assertEquals(user.timezone, 'UTC')
        self.assertTrue(user.check_password('supersikret42'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_manager_create_superuser(self):
        user = Customer.objects.create_superuser(
            email='filwaitman@gmail.com', password='supersikret42', name='Sloth', timezone='UTC'
        )
        self.assertEquals(user.email, 'filwaitman@gmail.com')
        self.assertEquals(user.name, 'Sloth')
        self.assertEquals(user.timezone, 'UTC')
        self.assertTrue(user.check_password('supersikret42'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
