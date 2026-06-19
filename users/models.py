from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from materials.models import Course, Lesson


class User(AbstractUser):
    """Класс пользователя"""

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="email",
    )
    phone = PhoneNumberField(
        max_length=25,
        verbose_name="Номер телефона",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    avatar = models.ImageField(
        upload_to="users/avatar", verbose_name="Аватар", blank=True, null=True, help_text="Загрузить аватар"
    )
    city = models.CharField(
        verbose_name="Город",
        help_text="Введите город",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Класс платежа"""

    CASH = "cash"
    TRANSFER = "transfer"
    STRIPE_TRANSFER = "stripe_transfer"

    PAYMENT_METHODS = [
        (CASH, "Оплата наличными"),
        (TRANSFER, "Перевод на счет"),
        (STRIPE_TRANSFER, "Stripe"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", verbose_name="Пользователь")
    date_payment = models.DateTimeField(
        verbose_name="Дата платежа",
        auto_now_add=True,
    )
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии", help_text="Укажите ID сессии"
    )
    link = models.URLField(
        max_length=600, blank=True, null=True, verbose_name="Ссылка на оплату", help_text="Укажите ссылку на оплату"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, default=STRIPE_TRANSFER, verbose_name="Способ оплаты"
    )
    status = models.CharField(max_length=20, blank=True, null=True, verbose_name="Статус платежа")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f'Дата платежа: {self.date_payment}'
