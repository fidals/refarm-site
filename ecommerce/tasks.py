from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail as django_send_mail

logger = get_task_logger(__name__)


@shared_task(ignore_result=False)
def send_mail(*args, **kwargs):
    logger.info(
        f'Send mail from: {kwargs.get("from_email", settings.EMAIL_SENDER)}'
        f' to {kwargs.get("recipient_list", "")}'
    )
    django_send_mail(*args, **kwargs)
