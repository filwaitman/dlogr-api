# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import arrow

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse

from main.models import Customer, Event
from main.tests.base import APITestCase, CustomerFactory, EventFactory


class CustomerAPITestCase(APITestCase):
    def test_list(self):
        response = self.client.get(reverse('customers-list'))
        self.assertEquals(response.status_code, 405)

    def test_list_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse('customers-list'))
        self.assertEquals(response.status_code, 401)

    def test_retrieve(self):
        response = self.client.get(reverse('customers-detail', kwargs={'pk': self.user.pk}))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['id'], str(self.user.id))
        self.assertEquals(response.data['name'], self.user.name)
        self.assertEquals(response.data['email'], self.user.email)
        self.assertEquals(arrow.get(response.data['created']), self.user.created)
        self.assertEquals(arrow.get(response.data['modified']), self.user.modified)

    def test_retrieve_someone_else(self):
        someone_else = CustomerFactory.create()
        response = self.client.get(reverse('customers-detail', kwargs={'pk': someone_else.pk}))
        self.assertEquals(response.status_code, 404)

    def test_retrieve_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse('customers-detail', kwargs={'pk': self.user.pk}))
        self.assertEquals(response.status_code, 401)

    def test_create(self):
        self.client.logout()
        mail.outbox = []

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'password': 'supersikret',
            'timezone': 'America/Sao_Paulo',
        }
        response = self.client.post(reverse('customers-list'), data)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['name'], 'Filipe Waitman')
        self.assertEquals(response.data['email'], 'filwaitman@gmail.com')

        user = Customer.objects.get(id=response.data['id'])
        self.assertEquals(user.name, 'Filipe Waitman')
        self.assertEquals(user.email, 'filwaitman@gmail.com')
        self.assertTrue(user.check_password('supersikret'))
        self.assertFalse(user.email_verified)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, u'[Dlogr] Account activation')

    def test_create_fields_consistency(self):
        self.client.logout()

        data = {
            'email': 'filwaitman@gmail.com',
            'password': 'supersikret',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['name'], [u'This field is required.'])

        data = {
            'name': '         ',
            'email': 'filwaitman@gmail.com',
            'password': 'supersikret',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['name'], [u'This field may not be blank.'])

        data = {
            'name': 'Filipe Waitman',
            'password': 'supersikret',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'This field is required.'])

        data = {
            'name': 'Filipe Waitman',
            'email': '  ',
            'password': 'supersikret',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'This field may not be blank.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'hamster',
            'password': 'supersikret',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'Enter a valid email address.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['password'], [u'This field is required.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'password': '   ',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['password'], [u'This field may not be blank.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'password': 'aa',
            'timezone': 'UTC',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['password'], [u'Ensure this field has at least 8 characters.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'password': 'supersikret',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['timezone'], [u'This field is required.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'password': 'supersikret',
            'timezone': '         ',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['timezone'], [u'"         " is not a valid choice.'])

        data = {
            'name': 'Filipe Waitman',
            'email': 'filwaitman@gmail.com',
            'password': 'supersikret',
            'timezone': 'INVALID',
        }
        response = self.client.post(reverse('customers-list'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['timezone'], [u'"INVALID" is not a valid choice.'])

    def test_update(self):
        data = {
            'name': 'New Name'
        }
        response = self.client.patch(reverse('customers-detail', kwargs={'pk': self.user.pk}), data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['name'], 'New Name')

        self.user.refresh_from_db()
        self.assertEquals(self.user.name, 'New Name')

    def test_update_someone_else(self):
        someone_else = CustomerFactory.create()

        data = {
            'name': 'New Name'
        }
        response = self.client.patch(reverse('customers-detail', kwargs={'pk': someone_else.pk}), data)
        self.assertEquals(response.status_code, 404)

    def test_update_logged_out(self):
        self.client.logout()

        data = {
            'name': 'New Name'
        }
        response = self.client.patch(reverse('customers-detail', kwargs={'pk': self.user.pk}), data)
        self.assertEquals(response.status_code, 401)

    def test_update_email(self):
        self.user.email_verified = True
        self.user.save()
        mail.outbox = []

        data = {
            'email': 'new@email.com'
        }
        response = self.client.patch(reverse('customers-detail', kwargs={'pk': self.user.pk}), data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['email'], 'new@email.com')

        self.user.refresh_from_db()
        self.assertEquals(self.user.email, 'new@email.com')
        self.assertFalse(self.user.email_verified)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, u'[Dlogr] Please verify your email')

    def test_destroy(self):
        response = self.client.delete(reverse('customers-detail', kwargs={'pk': self.user.pk}))

        self.assertEquals(response.status_code, 204)
        self.assertFalse(Customer.objects.filter(id=self.user.id).exists())

    def test_destroy_someone_else(self):
        someone_else = CustomerFactory.create()
        response = self.client.delete(reverse('customers-detail', kwargs={'pk': someone_else.pk}))
        self.assertEquals(response.status_code, 404)

    def test_destroy_logged_out(self):
        self.client.logout()
        response = self.client.delete(reverse('customers-detail', kwargs={'pk': self.user.pk}))
        self.assertEquals(response.status_code, 401)


class EventAPITestCase(APITestCase):
    def setUp(self):
        super(EventAPITestCase, self).setUp()
        self.event = EventFactory.create(customer=self.user)

    def test_list(self):
        response = self.client.get(reverse('events-list'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['count'], 1)
        self.assertEquals(response.data['results'][0]['id'], str(self.event.id))
        self.assertEquals(response.data['results'][0]['object_id'], self.event.object_id)
        self.assertEquals(response.data['results'][0]['object_type'], self.event.object_type)
        self.assertEquals(response.data['results'][0]['human_identifier'], self.event.human_identifier)
        self.assertEquals(response.data['results'][0]['message'], self.event.message)
        self.assertEquals(arrow.get(response.data['results'][0]['timestamp']), self.event.timestamp)
        self.assertEquals(arrow.get(response.data['results'][0]['created']), self.event.created)
        self.assertEquals(arrow.get(response.data['results'][0]['modified']), self.event.modified)

    def test_list_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse('events-list'))
        self.assertEquals(response.status_code, 401)

    def test_retrieve(self):
        response = self.client.get(reverse('events-detail', kwargs={'pk': self.event.pk}))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['id'], str(self.event.id))
        self.assertEquals(response.data['object_id'], self.event.object_id)
        self.assertEquals(response.data['object_type'], self.event.object_type)
        self.assertEquals(response.data['human_identifier'], self.event.human_identifier)
        self.assertEquals(response.data['message'], self.event.message)
        self.assertEquals(arrow.get(response.data['timestamp']), self.event.timestamp)
        self.assertEquals(arrow.get(response.data['created']), self.event.created)
        self.assertEquals(arrow.get(response.data['modified']), self.event.modified)

    def test_retrieve_someone_else(self):
        someone_else = EventFactory.create()
        response = self.client.get(reverse('events-detail', kwargs={'pk': someone_else.pk}))
        self.assertEquals(response.status_code, 404)

    def test_retrieve_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse('events-detail', kwargs={'pk': self.event.pk}))
        self.assertEquals(response.status_code, 401)

    def test_create(self):
        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['object_id'], data['object_id'])
        self.assertEquals(response.data['object_type'], data['object_type'])
        self.assertEquals(response.data['human_identifier'], data['human_identifier'])
        self.assertEquals(response.data['message'], data['message'])
        self.assertEquals(arrow.get(response.data['timestamp']), arrow.get(data['timestamp']))

        event = Event.objects.get(id=response.data['id'])
        self.assertEquals(event.customer, self.user)
        self.assertEquals(event.object_id, data['object_id'])
        self.assertEquals(event.object_type, data['object_type'])
        self.assertEquals(event.human_identifier, data['human_identifier'])
        self.assertEquals(event.message, data['message'])
        self.assertEquals(event.timestamp, arrow.get(data['timestamp']))

    def test_create_logged_out(self):
        self.client.logout()

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)

        self.assertEquals(response.status_code, 401)

    def test_create_fields_consistency(self):
        data = {
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['object_id'], [u'This field is required.'])

        data = {
            'object_id': '   ',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['object_id'], [u'This field may not be blank.'])

        data = {
            'object_id': 'abcd-efgh',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['object_type'], [u'This field is required.'])

        data = {
            'object_id': 'abcd-efgh',
            'object_type': '     ',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['object_type'], [u'This field may not be blank.'])

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['human_identifier'], [u'This field is required.'])

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': '',
            'message': 'User signed up',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['human_identifier'], [u'This field may not be blank.'])

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['message'], [u'This field is required.'])

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': '     ',
            'timestamp': '2016-01-01T12:13:14',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['message'], [u'This field may not be blank.'])

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(response.data['timestamp'], [u'This field is required.'])

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(
            response.data['timestamp'],
            [
                u'Datetime has wrong format. '
                'Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ]
        )

        data = {
            'object_id': 'abcdefgh',
            'object_type': 'users.models.User',
            'human_identifier': 'Filipe Waitman',
            'message': 'User signed up',
            'timestamp': '2016',
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEquals(
            response.data['timestamp'],
            [
                u'Datetime has wrong format. '
                'Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ]
        )

    def test_update(self):
        data = {
            'message': 'New message'
        }
        response = self.client.patch(reverse('events-detail', kwargs={'pk': self.event.pk}), data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['message'], 'New message')

        self.event.refresh_from_db()
        self.assertEquals(self.event.message, 'New message')

    def test_update_someone_else(self):
        someone_else = EventFactory.create()

        data = {
            'message': 'New message'
        }
        response = self.client.patch(reverse('events-detail', kwargs={'pk': someone_else.pk}), data)
        self.assertEquals(response.status_code, 404)

    def test_update_logged_out(self):
        self.client.logout()

        data = {
            'message': 'New message'
        }
        response = self.client.patch(reverse('events-detail', kwargs={'pk': self.event.pk}), data)
        self.assertEquals(response.status_code, 401)

    def test_destroy(self):
        response = self.client.delete(reverse('events-detail', kwargs={'pk': self.event.pk}))

        self.assertEquals(response.status_code, 204)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_destroy_someone_else(self):
        someone_else = EventFactory.create()
        response = self.client.delete(reverse('events-detail', kwargs={'pk': someone_else.pk}))
        self.assertEquals(response.status_code, 404)

    def test_destroy_logged_out(self):
        self.client.logout()
        response = self.client.delete(reverse('events-detail', kwargs={'pk': self.event.pk}))
        self.assertEquals(response.status_code, 401)


class DynamicFieldsMixinTestCase(APITestCase):
    def test_fields(self):
        data = {
            'fields': 'id,name,ignoreunknownfields',
        }
        response = self.client.get(reverse('customers-detail', kwargs={'pk': self.user.pk}), data)

        self.assertEquals(len(response.data.keys()), 2)
        self.assertTrue('id' in response.data)
        self.assertTrue('name' in response.data)

    def test_exclude(self):
        data = {
            'exclude': 'id,name,ignoreunknownfields',
        }
        response = self.client.get(reverse('customers-detail', kwargs={'pk': self.user.pk}), data)

        self.assertTrue('email' in response.data)
        self.assertFalse('id' in response.data)
        self.assertFalse('name' in response.data)

    def test_fields_and_exclude(self):
        data = {
            'fields': 'id,name,ignoreunknownfields',
            'exclude': 'id,name,ignoreunknownfields',
        }
        response = self.client.get(reverse('customers-detail', kwargs={'pk': self.user.pk}), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, [u'Provide "fields" or "exclude" - not both.'])


class LoginAPITestCase(APITestCase):
    def test_common(self):
        self.client.logout()

        data = {
            'email': self.user.email,
            'password': self.user_password,
        }
        response = self.client.post(reverse('users-login'), data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['auth_token'], self.user.auth_token.key)
        self.assertEquals(response.data['id'], str(self.user.id))
        self.assertEquals(response.data['name'], self.user.name)
        self.assertEquals(response.data['email'], self.user.email)
        self.assertEquals(arrow.get(response.data['created']), self.user.created)
        self.assertEquals(arrow.get(response.data['modified']), self.user.modified)

    def test_fields_consistency(self):
        self.client.logout()

        data = {
            'password': self.user_password,
        }
        response = self.client.post(reverse('users-login'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'This field is required.'])

        data = {
            'email': '   ',
            'password': self.user_password,
        }
        response = self.client.post(reverse('users-login'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'This field may not be blank.'])

        data = {
            'email': self.user.email,
        }
        response = self.client.post(reverse('users-login'), data)
        self.assertEquals(response.data['password'], [u'This field is required.'])

        data = {
            'email': self.user.email,
            'password': '   ',
        }
        response = self.client.post(reverse('users-login'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['password'], [u'This field may not be blank.'])

        data = {
            'email': self.user.email,
            'password': 'this is not the correct password, dude',
        }
        response = self.client.post(reverse('users-login'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], [u'Unable to login with credentials provided.'])


class VerifyAccountAPITestCase(APITestCase):
    def test_common(self):
        self.assertFalse(self.user.email_verified)

        data = {
            'token': self.user.set_cache_key(key_prefix=settings.CACHE_PREFIX['VERIFY_ACCOUNT']),
        }
        response = self.client.post(reverse('users-verify-account'), data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['auth_token'], self.user.auth_token.key)
        self.assertEquals(response.data['id'], str(self.user.id))
        self.assertEquals(response.data['name'], self.user.name)
        self.assertEquals(response.data['email'], self.user.email)

        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_fields_consistency(self):
        data = {
        }
        response = self.client.post(reverse('users-verify-account'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['token'], ['This field is required.'])
        self.assertFalse(self.user.email_verified)

        data = {
            'token': '',
        }
        response = self.client.post(reverse('users-verify-account'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['token'], ['This field may not be blank.'])
        self.assertFalse(self.user.email_verified)

    def test_invalid_key(self):
        data = {
            'token': 'invalid',
        }
        response = self.client.post(reverse('users-verify-account'), data)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], [u'Token is invalid (or has expired).'])
        self.assertFalse(self.user.email_verified)

    def test_expired_token(self):
        pass  # FIXME
        # with freeze_time(datetime(2016, 1, 1, 12, 12, 12)):
        #     self.assertFalse(self.user.email_verified)

        #     data = {
        #         'token': self.user.set_cache_key(key_prefix=settings.CACHE_PREFIX['VERIFY_ACCOUNT']),
        #     }

        # with freeze_time(datetime(2016, 1, 3, 12, 12, 12)):
        #     response = self.client.post(reverse('users-verify-account'), data)
        #     self.assertEquals(response.status_code, 400)
        #     self.assertEquals(response.data['non_field_errors'], [u'Token is invalid (or has expired).'])
        #     self.assertFalse(self.user.email_verified)


class ResetPasswordAPITestCase(APITestCase):
    def test_common(self):
        mail.outbox = []

        data = {
            'email': self.user.email,
        }
        response = self.client.post(reverse('users-reset-password'), data)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, u'[Dlogr] Reset your password')

    def test_fields_consistency(self):
        data = {
        }
        response = self.client.post(reverse('users-reset-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], ['This field is required.'])

        data = {
            'email': '    ',
        }
        response = self.client.post(reverse('users-reset-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], ['This field may not be blank.'])

        data = {
            'email': 'invalid',
        }
        response = self.client.post(reverse('users-reset-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'Enter a valid email address.'])

    def test_unknown_email(self):
        mail.outbox = []

        data = {
            'email': 'unknown@email.com',
        }
        response = self.client.post(reverse('users-reset-password'), data)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(len(mail.outbox), 0)


class ChangePasswordAPITestCase(APITestCase):
    def test_common_via_credentials(self):
        data = {
            'email': self.user.email,
            'password': self.user_password,
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['auth_token'], self.user.auth_token.key)
        self.assertEquals(response.data['id'], str(self.user.id))
        self.assertEquals(response.data['name'], self.user.name)
        self.assertEquals(response.data['email'], self.user.email)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('supersikret42'))

    def test_common_via_reset_token(self):
        data = {
            'reset_token': self.user.set_cache_key(key_prefix=settings.CACHE_PREFIX['RESET_PASSWORD']),
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['auth_token'], self.user.auth_token.key)
        self.assertEquals(response.data['id'], str(self.user.id))
        self.assertEquals(response.data['name'], self.user.name)
        self.assertEquals(response.data['email'], self.user.email)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('supersikret42'))

    def test_fields_consistency(self):
        data = {
            'password': self.user_password,
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Either reset_token or (email, password) is required.'])

        data = {
            'email': '    ',
            'password': self.user_password,
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Either reset_token or (email, password) is required.'])

        data = {
            'email': 'filwaitman@gmail.com',
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Either reset_token or (email, password) is required.'])

        data = {
            'email': 'filwaitman@gmail.com',
            'password': '  ',
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Either reset_token or (email, password) is required.'])

        data = {
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Either reset_token or (email, password) is required.'])

        data = {
            'reset_token': '  ',
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Either reset_token or (email, password) is required.'])

        data = {
            'email': 'fil',
            'password': self.user_password,
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['email'], [u'Enter a valid email address.'])

        data = {
            'email': 'filwaitman@gmail.com',
            'password': self.user_password,
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['new_password'], [u'This field is required.'])

        data = {
            'email': 'filwaitman@gmail.com',
            'password': self.user_password,
            'new_password': '   ',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['new_password'], [u'This field may not be blank.'])

    def test_invalid_credentials(self):
        data = {
            'email': self.user.email,
            'password': 'INVALID',
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Unable to login with credentials provided.'])

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('supersikret42'))

    def test_invalid_reset_token(self):
        data = {
            'reset_token': 'INVALID',
            'new_password': 'supersikret42',
        }
        response = self.client.post(reverse('users-change-password'), data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['non_field_errors'], ['Reset token is invalid (or has expired).'])

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('supersikret42'))
