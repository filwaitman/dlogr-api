# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Event, Customer
from main.serializers import (
    EventSerializer, CustomerSerializer, LoginSerializer, CustomerAuthenticatedSerializer, VerifyAccountSerializer,
    ResetPasswordSerializer, ChangePasswordSerializer
)


def handler500(request):
    from django.http import JsonResponse
    return JsonResponse({'detail': 'Sorry, Dlogr API is facing technical difficulties'}, status=500)


class BaseAPIMixin(object):
    pass


class CustomerAPI(BaseAPIMixin, viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self, *args, **kwargs):
        return Customer.objects.filter(id=self.request.user.id)

    def list(self, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny(), ]
        return super(CustomerAPI, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerAuthenticatedSerializer
        return super(CustomerAPI, self).get_serializer_class()


class EventAPI(BaseAPIMixin, viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_fields = ('object_id', 'object_type', 'human_identifier')
    search_fields = ('object_id', 'object_type', 'human_identifier', 'message')

    def get_queryset(self):
        return Event.objects.filter(customer=self.request.user)

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPI(BaseAPIMixin, APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_serializer = CustomerAuthenticatedSerializer(serializer.validated_data['user'])
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class VerifyAccountAPI(BaseAPIMixin, APIView):
    serializer_class = VerifyAccountSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.email_verified = True
        user.save()

        user_serializer = CustomerAuthenticatedSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class ResetPasswordAPI(BaseAPIMixin, APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = Customer.objects.filter(email__iexact=serializer.validated_data['email']).first()
        if user:
            user.send_reset_password_link_by_email()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ChangePasswordAPI(BaseAPIMixin, APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_serializer = CustomerAuthenticatedSerializer(serializer.validated_data['user'])
        return Response(user_serializer.data, status=status.HTTP_200_OK)
