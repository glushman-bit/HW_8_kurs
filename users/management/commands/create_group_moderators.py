from django.core.management import BaseCommand
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    """ Кастомная команда для создания группы 'moderators' с назначением необходимых прав. """
    help = "Создает группу 'Менеджеры' и назначает ей базовые права доступа"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='moderat')

        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'moderators' успешно создана."))
        else:
            self.stdout.write(self.style.WARNING("Группа 'moderators' уже существует."))

        course = ContentType.objects.get_for_model(Course)
        lesson = ContentType.objects.get_for_model(Lesson)

        permissions = Permission.objects.filter(
            codename__in=[
                "view_lesson",
                "change_lesson",
                "view_course",
                "change_course",
            ],
            content_type__in=[course, lesson],
        )

        group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS(
            f"Группе успешно назначено прав: {permissions.count()} шт.")
        )
