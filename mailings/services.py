from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import MailingAttempt


def send_mailing(mailing):
    """
    Отправляет письма всем получателям рассылки.
    Возвращает кортеж (успешных, неуспешных).
    """
    if not mailing.message:
        return 0, 0

    success_count = 0
    fail_count = 0

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                status='Успешно',
                server_response='Письмо отправлено',
                mailing=mailing,
            )
            success_count += 1
        except Exception as e:
            MailingAttempt.objects.create(
                status='Не успешно',
                server_response=str(e),
                mailing=mailing,
            )
            fail_count += 1

    return success_count, fail_count
