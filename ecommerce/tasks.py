from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail as django_send_mail

from ecommerce import mailer


@shared_task(ignore_result=True)
def send_mail(*args, **kwargs):
    django_send_mail(*args, **kwargs)
