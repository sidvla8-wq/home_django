# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Product
# from .forms import ProductForm
#
# def product_list(request):
#     products = Product.objects.all()
#     return render(request, "catalog/product_list.html", {"products": products})
#
# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     return render(request, "catalog/product_detail.html", {"product": product})
#
# def product_create(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect("product_list")
#     else:
#         form = ProductForm()
#     return render(request, "catalog/product_form.html", {"form": form, "action": "Создать"})
#
# def product_update(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect("product_detail", pk=product.pk)
#     else:
#         form = ProductForm(instance=product)
#     return render(request, "catalog/product_form.html", {"form": form, "action": "Редактировать"})
#
# def product_delete(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == "POST":
#         product.delete()
#         return redirect("product_list")
#     return render(request, "catalog/product_confirm_delete.html", {"product": product})

#

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Product
from .forms import ProductForm


class HomeView(ListView):
    """Главная — список товаров (открыто всем)"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'
    paginate_by = 3

    def get_queryset(self):
        # Анонимам и обычным юзерам — только опубликованные
        # Владельцам и модераторам — все
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or user.has_perm('catalog.can_unpublish_product')):
            return qs
        return qs.filter(is_published=True)


class ProductDetailView(DetailView):
    """Просмотр товара (открыто всем, но черновики — только владельцу/модератору)"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or user.has_perm('catalog.can_unpublish_product')):
            return qs
        return qs.filter(is_published=True)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'image', 'category', 'is_published']
    template_name = 'catalog/product_form.html'
    success_url = '/products/'

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Присваиваем владельца
        response = super().form_valid(form)

        # Сброс КЭШа при создании
        cache.delete('all_published_products')
        if form.instance.category:
            cache.delete(f'products_by_category_{form.instance.category_id}')

        return response


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'image', 'category', 'is_published']
    template_name = 'catalog/product_form.html'
    success_url = '/products/'  # или свой URL

    def test_func(self):
        # Разрешаем редактировать только владельцу или суперпользователю
        product = self.get_object()
        return self.request.user == product.owner or self.request.user.is_superuser

    def form_valid(self, form):
        response = super().form_valid(form)

        # 1. Сбрасываем кеш главной страницы (список всех товаров)
        cache.delete('all_published_products')

        # 2. Сбрасываем кеш категории, если она изменилась
        if self.object.category:
            cache.delete(f'products_by_category_{self.object.category_id}')

        return response


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('home')  # или свой URL
    template_name = 'catalog/product_confirm_delete.html'

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.owner or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()  # Сохраняем объект ДО удаления

        # Сброс КЭШа перед удалением
        cache.delete('all_published_products')
        if obj.category:
            cache.delete(f'products_by_category_{obj.category_id}')

        return super().delete(request, *args, **kwargs)


class ProductUnpublishView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Отмена публикации — только модератор"""
    model = Product
    fields = ['is_published']
    template_name = 'catalog/product_confirm_unpublish.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.request.user.has_perm('catalog.can_unpublish_product')

    def form_valid(self, form):
        form.instance.is_published = False
        form.instance.save()
        return super().form_valid(form)


class ContactView(TemplateView):
    template_name = 'catalog/contacts.html'

# Задание 29
from django.shortcuts import get_object_or_404
from .models import Category
from .services import get_cached_products_by_category
from .services import get_cached_products

class HomeView(ListView):
    """Главная — список товаров (открыто всем, с кешированием)"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'
    paginate_by = 3

    def get_queryset(self):
        return get_cached_products()

class ProductsByCategoryView(ListView):
    """Список продуктов в указанной категории (с кешированием)"""
    template_name = 'catalog/products_by_category.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        # Используем сервисную функцию с низкоуровневым кешированием (Задание 4)
        return get_cached_products_by_category(category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('pk')
        context['category'] = get_object_or_404(Category, pk=category_id)
        return context
