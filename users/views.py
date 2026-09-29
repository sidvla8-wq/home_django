from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import UpdateView, CreateView, TemplateView
from django.urls import reverse_lazy

from .models import User
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm


class UserLoginView(LoginView):
    """Авторизация по email"""
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def get_success_url(self):
        return reverse_lazy('home')


class UserLogoutView(LoginRequiredMixin, TemplateView):
    """Выход"""
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')


class UserRegisterView(CreateView):
    """Регистрация + приветственное письмо"""
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Отправка приветственного письма
        send_mail(
            subject='Добро пожаловать в SkyStore!',
            message=(
                f'Здравствуйте!\n\n'
                f'Вы успешно зарегистрировались в магазине SkyStore.\n'
                f'Ваш email: {self.object.email}\n\n'
                f'Спасибо, что выбрали нас!'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.object.email],
            fail_silently=True,
        )
        return response


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
    