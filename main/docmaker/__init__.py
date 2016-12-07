# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from collections import OrderedDict
from datetime import datetime
from io import IOBase
import json
import os
import re
import uuid

from freezegun import freeze_time
import jinja2

from django.conf import settings
from django.core.urlresolvers import reverse

from main.tests.base import APITestCase, EventFactory

now = datetime.now().isoformat()


def sort_dict(obj):
    if not isinstance(obj, dict):
        if hasattr(obj, '__iter__') and not isinstance(obj, str):
            result = []
            for x in obj:
                result.append(sort_dict(x))
            return result

        return obj

    result = []
    for key, value in sorted(dict(obj).items()):
        result.append((key, sort_dict(value)))

    return OrderedDict(result)


def json_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, IOBase):
        return '<file data>'
    else:
        raise TypeError


@freeze_time(datetime(2016, 11, 1, 12, 12, 12))
class DocMaker(APITestCase):
    def adapt_response(
        self, request_method, request_path,
        request_data=None, print_request=True, print_response=True, link_to_top=True, hr=True,
        **request_kwargs
    ):
        if not request_data:
            request_data = {}

        response = getattr(self.client, request_method)(request_path, request_data, **request_kwargs)

        request_data = json.dumps(sort_dict(request_data), indent=4, default=json_handler)
        response_data = json.dumps(sort_dict(response.data), indent=4, default=json_handler)

        result = '### Example:\n\n'

        if print_request:
            result += '''
#### Request:

**Fingerprint**: `{method} {path}`

**Payload**:
```
{data}
```
        '''.format(method=request_method.upper(), path=request_path, data=request_data)

        if print_response:
            result += '''
#### Response:

**Status code**: `{status_code}`

**Data**:
```
{data}
```
        '''.format(status_code=response.status_code, data=response_data)

        if link_to_top:
            result += '\n\n[back to top](#dlogr-api-documentation)'

        if hr:
            result += '\n\n---'

        return result

    def reset_modeling(self):
        fake_now = datetime.utcnow()

        self.user.name = 'Filipe Waitman'
        self.user.save()
        self.user_cache_key = self.user.set_cache_key(key_prefix=settings.CACHE_PREFIX['VERIFY_ACCOUNT'])

        self.event = EventFactory.create(
            customer=self.user,
            message='User made something',
            object_type='users.models.User',
            object_id='1234',
            human_identifier='Bart Simpson',
            timestamp=fake_now,
        )

    def test_docmaker(self):
        ''' TODO: Find a beter way to get a real documentation based on test engine/database '''
        if not(os.environ.get('DLOGR_DOCMAKER')):
            return

        self.reset_modeling()
        fake_now = datetime.utcnow()
        fake_uuid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
        customer_details_url = reverse('customers-detail', kwargs={'pk': self.user.pk})
        event_details_url = reverse('events-detail', kwargs={'pk': self.event.pk})
        cwd = os.getcwd()
        read_path = os.path.join(cwd, 'main', 'docmaker', 'api_doc_template.md')
        write_path = os.path.join(cwd, 'docs', 'api.md')

        with open(read_path) as f:
            template = jinja2.Template(f.read())

        context = {
            'updated_at': now,
        }

        # Auth
        data = {'email': self.user.email, 'password': self.user_password}
        context.update({'auth_login': self.adapt_response('post', reverse('users-login'), data)})

        data = {'token': self.user_cache_key}
        context.update({'auth_verify_account': self.adapt_response('post', reverse('users-verify-account'), data)})

        data = {'email': self.user.email}
        context.update({'auth_reset_password': self.adapt_response('post', reverse('users-reset-password'), data)})

        data = {'email': self.user.email, 'password': self.user_password, 'new_password': 'muchbetternow'}
        context.update({'auth_change_password': self.adapt_response('post', reverse('users-change-password'), data)})

        # Events
        context.update({'get_events_list': self.adapt_response('get', reverse('events-list'))})

        context.update({'get_events_detail': self.adapt_response('get', event_details_url)})

        data = {
            'message': 'User got mad', 'timestamp': fake_now,
            'object_type': 'users.models.User', 'object_id': '1234', 'human_identifier': 'Mr Anderson',
        }
        context.update({'post_events_list': self.adapt_response('post', reverse('events-list'), data)})

        data = {'message': 'Fixed message'}
        context.update({'patch_events_detail': self.adapt_response('patch', event_details_url, data)})

        context.update({'delete_events_detail': self.adapt_response('delete', event_details_url)})

        # Customers
        context.update({'get_customers_detail': self.adapt_response('get', customer_details_url)})

        data = {'email': 'filwaitman@gmail.com', 'password': 'answeris42', 'name': 'John Doe', 'timezone': 'UTC'}
        context.update({'post_customers_list': self.adapt_response('post', reverse('customers-list'), data)})

        data = {'name': 'Filipe Waitman Yet Again', 'timezone': 'America/Sao_Paulo'}
        context.update({'patch_customers_detail': self.adapt_response('patch', customer_details_url, data)})

        context.update({'delete_customers_detail': self.adapt_response('delete', customer_details_url)})

        content = template.render(**context)
        content = re.sub('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', fake_uuid, content)
        content = re.sub('[0-9a-f]{40}', 'X' * 40, content)
        content = re.sub('"http://testserver/.*page=.*"', 'null', content)
        content = re.sub('"http://testserver/.*"', '"<file URI>"', content)
        content = re.sub('"/tmp/.*"', '"<file URI>"', content)
        content = re.sub('4gn-[0-9a-f]{21}\.[0-9a-f]{12}', '<token>', content)

        with open(write_path, 'w') as f:
            f.write(content)
