import logging

from celery import shared_task
from django.core.mail import send_mail, send_mass_mail

from config import settings

logger = logging.getLogger(__name__)


@shared_task
def send_information_about_add_course(email, name):
    """Отправка сообщения пользователю о добавлении курса."""

    send_mail(
        subject=f'Добавлен курс {name}.',
        message=f'Обратите внимание! Вам добавлен новый курс {name}. '
        f'Для более подробной информации посетите сайт.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info('Письмо о добавлении курса отправлено.')


@shared_task
def send_information_about_update_course(email_list, course_name):
    """Отправка сообщения пользователю об изменения курса."""
    logger.info(f'Начало рассылки на {len(email_list)} адресов.')

    messages = []
    for email in email_list:
        message_data = (
            f'Курс "{course_name}" был обновлен.',
            f'Обратите внимание! Внесены изменения в курс {course_name}. '
            f'Для более подробной информации посетите сайт.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        messages.append(message_data)

    send_mass_mail(tuple(messages), fail_silently=False)

    logger.info('Письмо об изменении курса отправлено.')
