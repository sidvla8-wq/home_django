from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView,
)
from django.utils import timezone

from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing


# Главная страница

class HomeView(TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cache_key = 'home_stats'
        stats = cache.get(cache_key)
        if stats is None:
            now = timezone.now()
            total_mailings = Mailing.objects.count()
            active_mailings = Mailing.objects.filter(
                start_time__lte=now, end_time__gte=now, status='Запущена'
            ).count()
            unique_recipients = Recipient.objects.count()
            stats = {
                'total_mailings': total_mailings,
                'active_mailings': active_mailings,
                'unique_recipients': unique_recipients,
            }
            cache.set(cache_key, stats, 60 * 5)

        context.update(stats)
        return context


# Получатели

class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists() or user.is_superuser:
            return qs
        return qs.filter(owner=user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists() or user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def test_func(self):
        return self.get_object().owner == self.request.user


class RecipientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def test_func(self):
        return self.get_object().owner == self.request.user


# Сообщения

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists() or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists() or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def test_func(self):
        return self.get_object().owner == self.request.user


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')

    def test_func(self):
        return self.get_object().owner == self.request.user


# Рассылки (Mailings)

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists() or user.is_superuser:
            qs = Mailing.objects.all()
        else:
            qs = Mailing.objects.filter(owner=user)
        # Обновляем статус для каждой
        for m in qs:
            m.update_status()
        return qs


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists() or user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← динамический пересчёт статуса
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.all()[:20]
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        cache.delete('home_stats')
        return response


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        return self.get_object().owner == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete('home_stats')
        return response


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def test_func(self):
        return self.get_object().owner == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete('home_stats')
        return response


# Ручной запуск рассылки

class MailingSendView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'mailings/mailing_send_result.html'

    def test_func(self):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        return mailing.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        mailing.update_status()
        now = timezone.now()

        if not mailing.is_active:
            context['error'] = 'Рассылка отключена менеджером.'
            context['mailing'] = mailing
            return context

        if mailing.start_time <= now <= mailing.end_time:
            success, fail = send_mailing(mailing)
            context['success'] = success
            context['fail'] = fail
            context['mailing'] = mailing
            cache.delete('home_stats')
        else:
            context['error'] = (
                f'Отправка невозможна: текущее время {now:%d.%m.%Y %H:%M} '
                f'не входит в диапазон {mailing.start_time:%d.%m.%Y %H:%M} — '
                f'{mailing.end_time:%d.%m.%Y %H:%M}.'
            )
            context['mailing'] = mailing
        return context


# Статистика

class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        mailings = Mailing.objects.filter(owner=user)

        cache_key = f'stats_{user.pk}'
        stats = cache.get(cache_key)
        if stats is None:
            total_sent = MailingAttempt.objects.filter(mailing__in=mailings).count()
            success = MailingAttempt.objects.filter(
                mailing__in=mailings, status='Успешно'
            ).count()
            fail = MailingAttempt.objects.filter(
                mailing__in=mailings, status='Не успешно'
            ).count()
            stats = {
                'total_sent': total_sent,
                'success': success,
                'fail': fail,
            }
            cache.set(cache_key, stats, 60 * 5)

        context.update(stats)
        return context


# Блокировка пользователя (для менеджера)

class UserBlockView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.groups.filter(name='Менеджер').exists() or self.request.user.is_superuser

    def get(self, request, pk):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect('mailings:manager_user_list')


class ManagerUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'mailings/manager_user_list.html'
    context_object_name = 'users'
    model = None

    def test_func(self):
        return self.request.user.groups.filter(name='Менеджер').exists() or self.request.user.is_superuser

    def get_queryset(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(is_superuser=False)


class MailingToggleActiveView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Менеджер может отключать/включать рассылки."""
    def test_func(self):
        return self.request.user.groups.filter(name='Менеджер').exists() or self.request.user.is_superuser

    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = not mailing.is_active
        mailing.save(update_fields=['is_active'])
        cache.delete('home_stats')
        return redirect('mailings:mailing_list')
