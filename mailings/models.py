from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

STATUS_CHOICES = [
    ('Создана', 'Создана'),
    ('Запущена', 'Запущена'),
    ('Завершена', 'Завершена'),
]


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=200, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='recipients', verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Message(models.Model):
    subject = models.CharField(max_length=200, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='messages', verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-id']

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Создана', verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True,
        related_name='mailings', verbose_name='Сообщение'
    )
    recipients = models.ManyToManyField(
        Recipient, related_name='mailings', verbose_name='Получатели'
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='mailings', verbose_name='Владелец'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-start_time']

    def __str__(self):
        return f'Рассылка #{self.pk} — {self.start_time:%d.%m.%Y %H:%M}'

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time < timezone.now():
                raise ValidationError('Дата начала не может быть в прошлом.')
            if self.start_time >= self.end_time:
                raise ValidationError('Дата начала должна быть раньше даты окончания.')

    def update_status(self):
        """Динамически вычисляет и обновляет статус рассылки."""
        now = timezone.now()
        if now < self.start_time:
            new_status = 'Создана'
        elif self.start_time <= now <= self.end_time:
            new_status = 'Запущена'
        else:
            new_status = 'Завершена'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
        return new_status


class MailingAttempt(models.Model):
    ATTEMPT_STATUS = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=ATTEMPT_STATUS, verbose_name='Статус')
    server_response = models.TextField(blank=True, verbose_name='Ответ сервера')
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE,
        related_name='attempts', verbose_name='Рассылка'
    )

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f'{self.attempt_time:%d.%m.%Y %H:%M} — {self.status}'
    