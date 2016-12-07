# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import os

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def send_email(subject_template, email_html_template, email_txt_template, context, to):
    subject = render_to_string(subject_template, context)
    subject = '{} {}'.format(settings.EMAIL_SUBJECT_PREFIX, ' '.join(subject.splitlines()))  # Newlines not allowed.

    message_txt = render_to_string(email_txt_template, context)
    email_message = EmailMultiAlternatives(subject, message_txt, getattr(settings, 'DEFAULT_FROM_EMAIL'), [to, ])

    message_html = render_to_string(email_html_template, context)
    email_message.attach_alternative(message_html, 'text/html')

    email_message.send()


def send_email_plus(templates_path, context, to):
    subject_template = os.path.join(templates_path, 'subject.txt')
    email_html_template = os.path.join(templates_path, 'body.html')
    email_txt_template = os.path.join(templates_path, 'body.txt')

    send_email(
        subject_template=subject_template,
        email_html_template=email_html_template,
        email_txt_template=email_txt_template,
        context=context,
        to=to,
    )
