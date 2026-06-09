from django.core.management.base import BaseCommand
from django.utils import timezone

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    """Команда для добавления данных о платежах в базу данных."""

    help = "Добавление платежей в базу данных"

    def handle(self, *args, **options):
        Payment.objects.create(
            user=User.objects.first(),
            date_payment=timezone.now(),
            paid_course=Course.objects.first(),
            amount=5000,
            payment_method="cash",
        )
        Payment.objects.create(
            user=User.objects.first(),
            date_payment=timezone.now(),
            paid_lesson=Lesson.objects.first(),
            amount=1000,
            payment_method="transfer",
        )

        self.stdout.write(self.style.SUCCESS(f"Данные о платежах успешно добавлены"))
