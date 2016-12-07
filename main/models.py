# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
import random
import six.moves.urllib.parse
import uuid

from django_extensions.db.models import TimeStampedModel
import jsonfield
import pytz
from rest_framework.authtoken.models import Token

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from main.managers import CustomerManager
from main.utils import send_email_plus

logger = logging.getLogger(__name__)
TIMEZONE_CHOICES = [[x, x] for x in pytz.common_timezones]


class ModelBase(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True
        ordering = ('-created', )

    def get_old_instance(self):
        qs = getattr(self.__class__.objects, 'all_with_deleted', self.__class__.objects.all)()
        instance = qs.filter(id=self.id).first()

        if instance:
            instance.exists = True
            return instance

        instance = self.__class__()
        instance.exists = False
        return instance


@python_2_unicode_compatible
class Customer(ModelBase, AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    FIELDS_TO_EXCLUDE_ON_FULL_CLEAN = ('password', )

    email = models.EmailField(blank=False, null=False, unique=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=63, choices=TIMEZONE_CHOICES)

    objects = CustomerManager()

    def __str__(self):
        return '{}'.format(self.name)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def set_cache_key(self, key_prefix, time_to_live=None):
        token = default_token_generator.make_token(self)
        salt = str(random.random())
        key = token + salt
        full_key = '{}:{}'.format(key_prefix, key)

        if not time_to_live:
            time_to_live = settings.CACHE_DEFAULT_TIME_TO_LIVE_IN_SECONDS

        cache.set(full_key, self.pk, time_to_live)

        # Cache below is not really being used. It's here just for debugging purposes.
        full_debug_key = '{}:user:{}'.format(key_prefix, self.pk)
        cache.set(full_debug_key, key, settings.CACHE_DEFAULT_TIME_TO_LIVE_IN_SECONDS)

        logger.info('[Cache key] Setting value "{}" to customer "{}"'.format(key, str(self.pk)))
        return key

    def send_activation_link_by_email(self, just_joined=False):
        key = self.set_cache_key(key_prefix=settings.CACHE_PREFIX['VERIFY_ACCOUNT'])
        key = six.moves.urllib.parse.quote_plus(key)

        context = {
            'just_joined': just_joined,
            'activation_token': key,
            'customer': self,
            'url': settings.WEB_CLIENT_URLS['VERIFY_ACCOUNT'].format(key=key, joined=just_joined),
        }
        send_email_plus('emails/email_verification', context, self.email)

    def send_reset_password_link_by_email(self):
        key = self.set_cache_key(key_prefix=settings.CACHE_PREFIX['RESET_PASSWORD'])
        key = six.moves.urllib.parse.quote_plus(key)

        context = {
            'reset_token': key,
            'customer': self,
            'url': settings.WEB_CLIENT_URLS['RESET_PASSWORD'].format(key=key),
        }
        send_email_plus('emails/reset_password', context, self.email)

    def clean(self):
        self.email = self.email.lower()
        self.validate_unique()  # Run it once again in order to ensure there's no user with this email lowercased.
        return super(Customer, self).clean()

    def save(self, *args, **kwargs):
        old_instance = self.get_old_instance()

        if old_instance.email != self.email:
            self.email_verified = False
            self.send_activation_link_by_email(just_joined=not(old_instance.exists))

        return super(Customer, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Event(ModelBase):
    customer = models.ForeignKey(Customer, related_name='events')

    object_id = models.CharField(max_length=255, db_index=True)
    object_type = models.CharField(max_length=255, db_index=True)
    human_identifier = models.CharField(max_length=255, db_index=True)

    timestamp = models.DateTimeField(db_index=True)
    message = models.CharField(max_length=255, db_index=True)

    metadata = jsonfield.JSONField(blank=True, null=True)

    class Meta(object):
        ordering = ('-timestamp',)

    def __str__(self):
        return '{}/{} at {}: {}'.format(self.object_type, self.object_id, self.timestamp, self.message)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def customer_post_save(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save)
def regular_pre_save(instance, *args, **kwargs):
    app = instance.__class__.__module__.split('.')[0]
    if app not in settings.INTERNAL_APPS:
        return  # Don't mess with someone else's sanity.

    exclude = getattr(instance, 'FIELDS_TO_EXCLUDE_ON_FULL_CLEAN', [])
    instance.full_clean(exclude=exclude)
