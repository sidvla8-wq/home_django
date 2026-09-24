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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Product, Category
from .forms import ProductForm


class HomeView(ListView):
    """Главная — список товаров (открыто всем)"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'
    paginate_by = 3


class ProductDetailView(DetailView):
    """Просмотр товара (открыто всем)"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание товара (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('home')

    # Если нужно, чтобы товар привязывался к автору:
    # def form_valid(self, form):
    #     form.instance.owner = self.request.user
    #     return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование товара (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('home')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление товара (только для авторизованных)"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('home')


class ContactView(TemplateView):
    template_name = 'catalog/contacts.html'
