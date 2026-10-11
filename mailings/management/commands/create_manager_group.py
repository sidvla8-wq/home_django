from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Mailing, Recipient, Message


class Command(BaseCommand):
    help = 'Создаёт группу "Менеджер" с правами просмотра всех рассылок'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджер')

        models = [Mailing, Recipient, Message]
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            # Только просмотр
            view_perms = perms.filter(codename__startswith='view_')
            group.permissions.add(*view_perms)

        self.stdout.write(
            self.style.success(f'Группа "Менеджер" {"создана" if created else "обновлена"}.')
        )
