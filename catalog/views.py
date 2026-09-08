from django.shortcuts import render
from .models import Product

# def home(request):
#     """Контроллер для отображения домашней страницы (каталог)."""
#     return render(request, "catalog/home.html")


def home(request):
    latest_products = Product.objects.order_by('-created_at')[:5]
    print(latest_products)  # вывод в консоль сервера
    return render(request, 'catalog/home.html', {'products': latest_products})

def contacts(request):
    """Контроллер для отображения страницы контактов и обработки формы."""
    success = False
    if request.method == "POST":
        # Достаём данные из формы
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        # Выводим в консоль (позже можно сохранять в БД или отправлять на почту)
        print("--- Новое сообщение из формы ---")
        print(f"Имя:    {name}")
        print(f"Телефон: {phone}")
        print(f"Сообщение: {message}")
        print("--------------------------------")
        success = True
    return render(request, "catalog/contacts.html", {"success": success})

# def contacts(request):
#     contacts_list = Contact.objects.all()
#     return render(request, 'catalog/contacts.html', {'contacts': contacts_list})
