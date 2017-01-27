"""Contain functions to send eCommerce emails."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_order(
        *,
        template='ecommerce/order/email.html',
        subject=None,
        order=None,
        to_customer=True,
        to_shop=True,
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

    send_mail(
        subject=subject.format(order),
        message=email_template,
        from_email=settings.EMAIL_SENDER,
        recipient_list=recipients,
        html_message=email_template
    )


def send_backcall(*, template='ecommerce/order/backcall_email.html', subject, **fields):
    """Send mail about ordered backcall to shop."""

    message = render_to_string(template, {'fields': fields})

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_SENDER,
        recipient_list=[settings.EMAIL_RECIPIENT],
        html_message=message
    )


def ya_feedback(user_email):
    """Send email to user with Ya.Market feedback request."""

    email_template = render_to_string('ecommerce/yandex_feedback.html')

    send_mail(
        subject=settings.EMAIL_SUBJECTS['ya_feedback_request'],
        message=email_template,
        from_email=settings.EMAIL_SENDER,
        recipient_list=[user_email],
        html_message=email_template
    )
