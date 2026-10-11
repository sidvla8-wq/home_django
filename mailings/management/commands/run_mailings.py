from django.core.management.base import BaseCommand
from django.utils import timezone
from mailings.models import Mailing
from mailings.services import send_mailing


class Command(BaseCommand):
    help = 'Запускает все активные рассылки, у которых наступило время'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
        )

        count = 0
        for mailing in mailings:
            mailing.update_status()
            success, fail = send_mailing(mailing)
            count += 1
            self.stdout.write(
                f'Рассылка #{mailing.pk}: успешно — {success}, неуспешно — {fail}'
            )

        if count == 0:
            self.stdout.write('Нет рассылок для отправки.')
        else:
            self.stdout.write(self.style.SUCCESS(f'Обработано рассылок: {count}'))
            