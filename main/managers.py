# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging

from django.contrib.auth.models import BaseUserManager
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CustomerManager(BaseUserManager):
    def _create_user(self, email, password, name, is_staff=False, is_superuser=False, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, name=name, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, name, **extra_fields):
        return self._create_user(email, password, name, False, False, **extra_fields)

    def create_superuser(self, email, password, name, **extra_fields):
        return self._create_user(email, password, name, True, True, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)

    def get_from_cache_key(self, key, key_prefix):
        logger.info('[Cache key] Looking for value "{}"'.format(key))
        full_key = '{}:{}'.format(key_prefix, key)

        user_pk = cache.get(full_key)
        if not user_pk:
            return

        return self.model.objects.filter(pk=user_pk).first()  # Possibly None.
