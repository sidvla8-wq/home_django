from django.core.cache import cache
from .models import Product


def get_products_by_category(category_id):
    """Возвращает список всех продуктов в указанной категории"""
    return Product.objects.filter(category_id=category_id, is_published=True)


def get_cached_products_by_category(category_id):
    """
    Возвращает список продуктов по категории с использованием
    низкоуровневого кеширования (Задание 4).
    """
    cache_key = f'products_by_category_{category_id}'
    products = cache.get(cache_key)

    if products is None:
        products = list(get_products_by_category(category_id))
        cache.set(cache_key, products, timeout=60 * 15)  # 15 минут
        # Лог для проверки (в реальном проекте убери)
        print(f'--- Кеш промах, загружаем из БД для категории {category_id} ---')
    else:
        print(f'--- Кеш попадание для категории {category_id} ---')

    return products

def get_cached_products():
    """
    Возвращает список всех опубликованных продуктов с низкоуровневым
    кешированием (для главной страницы).
    """
    cache_key = 'all_published_products'
    products = cache.get(cache_key)

    if products is None:
        products = list(Product.objects.filter(is_published=True))
        cache.set(cache_key, products, timeout=60 * 15)
        print('--- Кеш промах, загружаем все продукты из БД ---')
    else:
        print('--- Кеш попадание для всех продуктов ---')

    return products
