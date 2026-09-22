# from django.shortcuts import render
# from django.shortcuts import get_object_or_404, render, redirect
# from django.core.paginator import Paginator
# from .models import Product
# from .forms import ProductForm
#
#
# def home(request):
#     """Главная страница со списком товаров (Задача 2 + пагинация)"""
#     products = Product.objects.all()
#     paginator = Paginator(products, 3)  # по 3 товара на страницу
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'catalog/home.html', {'page_obj': page_obj})
#
#
# def product_detail(request, pk):
#     """Страница с подробной информацией о товаре (Задача 1)"""
#     product = get_object_or_404(Product, pk=pk)
#     return render(request, 'catalog/product_detail.html', {'product': product})
#
# def home(request):
#     """Контроллер для отображения домашней страницы (каталог)."""
#     return render(request, "catalog/home.html")
#
#
# def contacts(request):
#     """Контроллер для отображения страницы контактов и обработки формы."""
#     success = False
#     if request.method == "POST":
#         # Достаём данные из формы
#         name = request.POST.get("name")
#         phone = request.POST.get("phone")
#         message = request.POST.get("message")
#         # Выводим в консоль (позже можно сохранять в БД или отправлять на почту)
#         print("--- Новое сообщение из формы ---")
#         print(f"Имя:    {name}")
#         print(f"Телефон: {phone}")
#         print(f"Сообщение: {message}")
#         print("--------------------------------")
#         success = True
#     return render(request, "catalog/contacts.html", {"success": success})
#
# def product_create(request):
#     """Форма добавления нового товара (доп. задание)"""
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = ProductForm()
#
#     return render(request, 'catalog/product_form.html', {'form': form})

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Product, Category
from .forms import ProductForm


class HomeView(ListView):
    """Главная страница — список товаров с пагинацией"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'
    paginate_by = 3


class ProductDetailView(DetailView):
    """Страница товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(CreateView):
    """Создание товара"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('home')


class ProductUpdateView(UpdateView):
    """Редактирование товара"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('home')


class ProductDeleteView(DeleteView):
    """Удаление товара"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('home')


class ContactView(TemplateView):
    """Страница контактов — через TemplateView"""
    template_name = 'catalog/contacts.html'
