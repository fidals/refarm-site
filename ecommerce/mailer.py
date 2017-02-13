"""Contain functions to send eCommerce emails."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from ecommerce.tasks import send_mail as celery_send_mail


def send(use_celery=False, *args, **kwargs):
    if use_celery:
        celery_send_mail.delay(*args, **kwargs)
    else:
        send_mail(*args, **kwargs)


def send_order(
        *,
        template='ecommerce/order/email.html',
        subject=None,
        order=None,
        to_customer=True,
        to_shop=True,
        use_celery=False,
        **extra_context
):
    """
    Send email with Order information.

    Accept a bunch of only-keyword args. Client code able to specify:
    - template which will be a body for email.
    - subject of an email (format-string in which order instance will be passed)
    - order instance
    - whether to send a letter to the customer and to the shop
    - extra content, which will be used while rendering the template. By default,
    template will receive only order instance.
    """

    template_context = {'order': order, **extra_context}
    email_template = render_to_string(template, template_context)
    recipients = []

    if to_customer:
        recipients.append(order.email)
    if to_shop:
        recipients.append(settings.EMAIL_RECIPIENT)

    send(
        use_celery=use_celery,
        subject=subject.format(order),
        message=email_template,
        from_email=settings.EMAIL_SENDER,
        recipient_list=recipients,
        html_message=email_template
    )


def send_backcall(*, template='ecommerce/order/backcall_email.html', subject, use_celery=False,**fields):
    """Send mail about ordered backcall to shop."""

    message = render_to_string(template, {'fields': fields})

    send(
        use_celery=use_celery,
        subject=subject,
        message=message,
        from_email=settings.EMAIL_SENDER,
        recipient_list=[settings.EMAIL_RECIPIENT],
        html_message=message
    )


def ya_feedback(user_email, use_celery=False):
    """Send email to user with Ya.Market feedback request."""

    email_template = render_to_string('ecommerce/yandex_feedback.html')

    send(
        use_celery=use_celery,
        subject=settings.EMAIL_SUBJECTS['ya_feedback_request'],
        message=email_template,
        from_email=settings.EMAIL_SENDER,
        recipient_list=[user_email],
        html_message=email_template
    )
