import logging

from celery import shared_task
from django.core.mail import send_mail

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
def send_information_about_update_course(email, name):
    """Отправка сообщения пользователю об изменения курса."""

    send_mail(
        subject=f'Курс "{name}" был обновлен.',
        message=f'Обратите внимание! Внесены изменения в курс {name}. '
        f'Для более подробной информации посетите сайт.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info('Письмо об изменении курса отправлено.')


@shared_task
def send_information_about_add_lesson(email, name, course_name):
    """Отправка сообщения пользователю о добавлении урока."""

    send_mail(
        subject=f'Добавлен урок {name}.',
        message=f'Обратите внимание! Вам добавлен новый урок {name} в курс {course_name}. '
        f'Для более подробной информации посетите сайт.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info('Письмо о добавлении урока отправлено.')


@shared_task
def send_information_about_update_lesson(email, name, course_name):
    """Отправка сообщения пользователю об изменении урока."""

    send_mail(
        subject=f'Информация об уроке {name}.',
        message=f'Обратите внимание! Информация об уроке {name} курса {course_name} изменилась. '
        f'Для более подробной информации посетите сайт.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info('Письмо об изменении урока отправлено.')
