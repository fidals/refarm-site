from django.conf import settings
from django.test import TestCase
from django.core import mail

from ecommerce import mailer
from ecommerce.models import Order


class TestMailer(TestCase):
    """Test cases for mailer module."""

    @classmethod
    def setUpClass(cls):
        """Set up testing Order instance."""
        super(TestMailer, cls).setUpClass()
        cls.order = Order(
            name='John Doe',
            email='test@test.test',
            phone='222222222222'
        )

    def test_mail_send_works(self):
        """If we send email, Django will put it in mail.outbox collection."""
        for i in range(10):
            mailer.send_order(
                subject='Testing email',
                order=self.order,
            )
        self.assertEqual(len(mail.outbox), i + 1)

    def test_mailer_construct_valid_email(self):
        """Saved email contains valid subject and valid body."""
        mailer.send_order(
            subject='Testing email 1',
            order=self.order,
        )
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, 'Testing email 1')
        self.assertIn('Thank you, {}'.format(self.order.name), sent_mail.body)

    def test_mailer_will_send_order_to_specified_recipients(self):
        """Saved email contains valid set of recipients."""
        mailer.send_order(
            subject='Testing email 1',
            order=self.order,
        )
        sent_mail = mail.outbox[0]
        recipients = [self.order.email]
        recipients.extend(settings.EMAIL_RECEPIENTS.split(','))
        self.assertListEqual(recipients, sent_mail.recipients())
        mailer.send_order(
            subject='Testing email 1',
            order=self.order,
            to_customer=False
        )
        sent_mail = mail.outbox[1]
        recipients = settings.EMAIL_RECEPIENTS.split(',')
        self.assertListEqual(recipients, sent_mail.recipients())

    def test_order_call(self):
        """Mailer module should be able to send mails about ordered calls."""

        subject = 'Testing backcall'
        mailer.send_backcall(
            subject=subject,
            phone='22222222',
            url='fidals.ru'
        )
        sent_mail = mail.outbox[0]
        recipients = [settings.SHOP_EMAIL]

        self.assertListEqual(recipients, sent_mail.recipients())
        self.assertEqual(sent_mail.subject, subject)
