from django.shortcuts import render


def home(request):
    """Контроллер для отображения домашней страницы (каталог)."""
    return render(request, "catalog/home.html")


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
