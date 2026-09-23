from django import forms
from django.core.exceptions import ValidationError
from .models import Product

FORBIDDEN_WORDS = [
    "казино", "криптовалюта", "крипта", "биржа",
    "дешево", "бесплатно", "обман", "полиция", "радар"
]

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]

def contains_forbidden_word(text):
    if not text:
        return False
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return True
    return False

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите название продукта"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Описание продукта"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Цена в рублях"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Можно дополнительно кастомизировать классы или атрибуты здесь,

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if contains_forbidden_word(name):
            raise ValidationError("Название содержит запрещённое слово.")
        return name

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if contains_forbidden_word(description):
            raise ValidationError("Описание содержит запрещённое слово.")
        return description

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
        return price

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image

        # Проверка размера
        if image.size > MAX_FILE_SIZE:
            raise ValidationError("Файл слишком большой. Максимальный размер — 5 МБ.")

        # Проверка типа контента
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationError("Разрешены только файлы JPEG и PNG.")

        return image
