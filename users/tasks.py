import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_user_is_active():
    """
    Проверка активности пользователей.
    Блокирует пользователей, если пользователь не активен в течение 30 дней
    или если пользователь зарегистрировался более 30 дней назад и ни разу не вошел.
    """
    User = get_user_model()

    one_month_ago = timezone.now() - timedelta(days=30)
    # count = get_user_model().objects.filter(last_login__lte=one_month_ago, is_active=True).update(is_active=False)
    activity_filter = Q(last_login__lte=one_month_ago) | Q(last_login__isnull=True, date_joined__lte=one_month_ago)
    count = User.objects.filter(
        activity_filter,
        is_active=True,
        is_superuser=False,
        is_staff=False,
    ).update(is_active=False)
    logger.info(f'Пользователи в количестве {count} не активны.')
