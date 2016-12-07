# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from rest_framework import routers

from main.api import EventAPI, CustomerAPI

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'events', EventAPI, base_name='events')
router.register(r'customers', CustomerAPI, base_name='customers')
