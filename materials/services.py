from datetime import timedelta

from django.utils import timezone

from materials.models import Course, Subscription
from materials.tasks import send_information_about_update_course


def notify_subscribes(course_id, old_updated_at):
    """
    Проверяет таймер курса по course_id.
    Если прошло > 4 часов, обновляет курс и запускает Celery tasks.py
    """

    now = timezone.now()

    if (now - old_updated_at) > timedelta(minutes=2):

        Course.objects.filter(pk=course_id).update(updated_at=now)

        email_list = list(
            Subscription.objects.filter(course_id=course_id, user__is_active=True)
            .values_list('user__email', flat=True)
        )

        if email_list:
            course_name = Course.objects.filter(pk=course_id).values_list('name', flat=True).first()
            send_information_about_update_course.delay(
                email_list=email_list,
                course_name=course_name
            )
        else:
            print("Прошло слишком мало времени с прошлого обновления. Рассылка пропущена.")
