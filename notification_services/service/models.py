import pytz
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import datetime
class Client(models.Model):
    TIME_ZONE = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    phone_validator = RegexValidator(
        regex=r'^7\d{10}$',
        message="Номер телефона в формате 7 XXX XXXXXXX (X - цифра от 0 до 9)")
    phone_number = models.CharField(validators=[phone_validator], max_length=11, unique=True, verbose_name='Номер клиента')
    mobile_operator_code = models.CharField(max_length=3,  blank=True, verbose_name='Код мобильного оператора')
    tag = models.CharField(max_length=50, verbose_name='Тег')
    timezone = models.CharField(max_length=32, choices=TIME_ZONE, default='UTS')

    def save(self, *args, **kwargs):
        self.mobile_operator_code = self.phone_number[1:4]
        super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.mobile_operator_code} - код оператора, {self.tag} - тег пользователя'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class Mailing(models.Model):
    date_start = models.DateTimeField(verbose_name='Дата начала рассылки')
    date_finish = models.DateTimeField(verbose_name='Дата окончания рассылки')
    text = models.TextField(verbose_name='Текст рассылки')
    mobile_code = models.CharField(null=True, blank=True,max_length=3, verbose_name='Фильтр по коду')
    client_tag = models.CharField(null=True, blank=True,max_length=50, verbose_name='Фильтр по тегу')
    time_interval_start = models.TimeField(verbose_name='Начало интервала, когда можно отправлять сообщения')
    time_interval_finish = models.TimeField(verbose_name='Конец интервала, когда можно отправлять сообщения')

    @property
    def send(self):
        return self.date_start <= timezone.now() <= self.date_finish

    def __str__(self):
        return f'{self.date_start.time()} {self.date_finish.time()}'

    class Meta:
        verbose_name='Рассылка'
        verbose_name_plural='Рассылки'

class Message(models.Model):
    STATUS = [
        ('Sent','Sent'),
        ('Not sent', 'Not sent'),
        ('Failed', 'Failed')
    ]
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(max_length=20, choices=STATUS, verbose_name='Статус')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='message', verbose_name="Клиент")
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='message', verbose_name="Рассылка")

    def __str__(self):
        return f'Сообщение клиенту {self.client}, статус {self.status}'

    class Meta:
        verbose_name='Сообщение'
        verbose_name_plural='Сообщения'
