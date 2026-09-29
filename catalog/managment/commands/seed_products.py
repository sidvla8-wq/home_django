from django.core.management.base import BaseCommand
from catalog.models import Product, Category


class Command(BaseCommand):
    help = 'Удаляет старые данные и добавляет тестовые продукты'

    def handle(self, *args, **kwargs):
        # Очищаем старые данные
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Создаём категории
        cat1 = Category.objects.create(name='Электроника', description='Гаджеты')
        cat2 = Category.objects.create(name='Книги', description='Печатные издания')

        # Создаём продукты
        Product.objects.create(name='Планшет', description='10 дюймов', category=cat1, price=25000)
        Product.objects.create(name='Наушники', description='Беспроводные', category=cat1, price=5000)
        Product.objects.create(name='Роман', description='Бестселлер', category=cat2, price=800)
        Product.objects.create(name='Учебник', description='По Python', category=cat2, price=1500)

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно добавлены!'))