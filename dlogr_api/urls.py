# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.contrib import admin

from main.api import LoginAPI, VerifyAccountAPI, ResetPasswordAPI, ChangePasswordAPI
from dlogr_api.routers import router

handler500 = 'main.api.handler500'

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r"^api/auth/login$", LoginAPI.as_view(), name="users-login"),
    url(r"^api/auth/verify-account$", VerifyAccountAPI.as_view(), name="users-verify-account"),
    url(r"^api/auth/reset-password$", ResetPasswordAPI.as_view(), name="users-reset-password"),
    url(r"^api/auth/change-password$", ChangePasswordAPI.as_view(), name="users-change-password"),

    url(r'^api/', include(router.urls)),
]
