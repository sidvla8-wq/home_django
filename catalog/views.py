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
    """Создание товара — автоматически привязывает владельца"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование — только владелец"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        product = self.get_object()
        return product.owner == self.request.user


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление — владелец ИЛИ модератор"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        product = self.get_object()
        is_owner = product.owner == self.request.user
        is_moderator = self.request.user.has_perm('catalog.delete_product')
        return is_owner or is_moderator


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
