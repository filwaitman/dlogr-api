# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from rest_framework import serializers, exceptions

from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import authenticate

from main.models import Event, Customer


class DynamicFieldsMixin(object):
    """
    Adapted from http://stackoverflow.com/a/23674297 / https://gist.github.com/dbrgn/4e6fc1fe5922598592d6
    A Serializer that takes an additional `fields` argument that controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        if not self.context:
            return  # During initialization this may happen

        fields = set([x for x in self.context['request'].query_params.get('fields', '').split(',') if x.strip()])
        exclude = set([x for x in self.context['request'].query_params.get('exclude', '').split(',') if x.strip()])
        initial_fields = set(self.fields.keys())

        if fields and exclude:
            raise serializers.ValidationError('Provide "fields" or "exclude" - not both.')

        elif fields:
            for field_name in initial_fields - fields:
                self.fields.pop(field_name)

        elif exclude:
            for field_name in exclude:
                self.fields.pop(field_name, None)


class ModelSanityMixin(object):
    FULL_CLEAN_EXCLUDE = None

    def validate(self, data):
        if self.Meta.model:  # If it's a ModelSerializer
            if self.instance:
                instance = self.instance
                for key, value in list(data.items()):
                    setattr(instance, key, value)
            else:
                instance = self.Meta.model(**data)

            try:
                instance.full_clean(self.FULL_CLEAN_EXCLUDE)
            except ValidationError as e:
                if e.message_dict:
                    raise exceptions.ValidationError(e.message_dict)
                raise exceptions.ValidationError(e.message)

        return super(ModelSanityMixin, self).validate(data)


class BaseSerializerMixin(ModelSanityMixin, DynamicFieldsMixin):
    pass


class EventSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    FULL_CLEAN_EXCLUDE = ['customer', ]

    class Meta:
        model = Event
        exclude = ('customer', )
        read_only_fields = ('id', 'created', 'modified')


class CustomerSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, min_length=8)

    class Meta:
        model = Customer
        fields = ('id', 'created', 'modified', 'email', 'name', 'password', 'timezone')
        read_only_fields = ('id', 'created', 'modified')

    def create(self, validated_data):
        return Customer.objects._create_user(**validated_data)


class CustomerAuthenticatedSerializer(CustomerSerializer):
    auth_token = serializers.ReadOnlyField(source='auth_token.key', read_only=True)

    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + ('auth_token', )
        read_only_fields = CustomerSerializer.Meta.read_only_fields + ('auth_token', )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Unable to login with credentials provided.')

        data["user"] = user
        return data


class VerifyAccountSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        customer = Customer.objects.get_from_cache_key(
            data.get('token'), key_prefix=settings.CACHE_PREFIX['VERIFY_ACCOUNT']
        )
        if not customer:
            raise serializers.ValidationError('Token is invalid (or has expired).')

        data['user'] = customer
        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    new_password = serializers.CharField()

    def validate(self, data):
        if not data.get('reset_token') and not all([data.get('email'), data.get('password')]):
            raise serializers.ValidationError('Either reset_token or (email, password) is required.')

        if data.get('reset_token'):
            customer = Customer.objects.get_from_cache_key(
                data.get('reset_token'), key_prefix=settings.CACHE_PREFIX['RESET_PASSWORD']
            )
            if not customer:
                raise serializers.ValidationError('Reset token is invalid (or has expired).')

        else:
            customer = authenticate(username=data.get('email'), password=data.get('password'))
            if not customer:
                raise serializers.ValidationError('Unable to login with credentials provided.')

        customer.set_password(data.get('new_password'))
        customer.save()
        data['user'] = customer
        return data
