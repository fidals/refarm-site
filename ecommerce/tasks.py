from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail as django_send_mail

logger = get_task_logger(__name__)


@shared_task(
    # a task will be acknowledged after the task has been executed,
    # not just before (the default behavior) to reach reliability
    acks_late=True,
)
def send_mail(*args, **kwargs):
    logger.info(
        f'Send mail from: {kwargs.get("from_email", settings.EMAIL_SENDER)}'
        f' to {", ".join(kwargs.get("recipient_list", []))}'
    )
    django_send_mail(*args, **kwargs)
