from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Article
from .forms import ArticleForm


class ArticleListView(ListView):
    """Список статей — только опубликованные (Задача 3: фильтрация)"""
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 5

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class ArticleDetailView(DetailView):
    """Просмотр статьи — увеличение счётчика просмотров (Задача 3)"""

    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save()

        # Доп. задание: отправка письма при 100 просмотрах
        if obj.views_count == 100:
            send_mail(
                subject='Поздравляем! 100 просмотров!',
                message=f'Статья «{obj.title}» достигла 100 просмотров!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )

        return obj


class ArticleCreateView(CreateView):
    """Создание статьи"""
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('blog:article_list')


class ArticleUpdateView(UpdateView):
    """Редактирование статьи — редирект на просмотр (Задача 3)"""
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'

    def get_success_url(self):
        return reverse_lazy('blog:article_detail', kwargs={'pk': self.object.pk})


class ArticleDeleteView(DeleteView):
    """Удаление статьи"""
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('blog:article_list')
