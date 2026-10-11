from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создаёт группы "Модератор продуктов" и "Контент-менеджер" с нужными правами'

    def handle(self, *args, **options):
        # --- Группа "Модератор продуктов" ---
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        content_type = ContentType.objects.get_for_model(Product)
        # Кастомное право — отмена публикации
        unpublish_perm = Permission.objects.get(content_type=content_type, codename='can_unpublish_product')
        # Право на удаление любого продукта
        delete_perm = Permission.objects.get(content_type=content_type, codename='delete_product')

        moderator_group.permissions.add(unpublish_perm, delete_perm)

        # --- Группа "Контент-менеджер" (доп. задание) ---
        from blog.models import Article
        blog_content_type = ContentType.objects.get_for_model(Article)
        blog_perms = Permission.objects.filter(content_type=blog_content_type)

        content_group, created = Group.objects.get_or_create(name='Контент-менеджер')
        content_group.permissions.set(blog_perms)

        self.stdout.write(self.style.SUCCESS('Группы успешно созданы!'))
        self.stdout.write(f'  Модератор продуктов: {moderator_group.permissions.count()} прав')
        self.stdout.write(f'  Контент-менеджер: {content_group.permissions.count()} прав')
