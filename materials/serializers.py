from rest_framework.fields import URLField, EmailField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson
from materials.validators import VideoUrlValidator


class LessonSerializer(ModelSerializer):
    """Сериализатор уроков"""

    owner_email = EmailField(source="owner.email", read_only=True)
    video_url = URLField(
        validators=[VideoUrlValidator()],
        required=False,
        allow_blank=True,
        allow_null=True,
        error_messages={
            "invalid": "Введена не корректная ссылка."
        }
    )

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "name",
            "description",
            "video_url",
            "owner_email",
        )


class CourseSerializer(ModelSerializer):
    """Сериализатор вывода информации о курсах.
    Подсчет количества уроков, уроки и их владельца."""

    count_lessons = SerializerMethodField()
    owner_email = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons(self, lessons):
        """Подсчет количества уроков на курсе"""

        return Lesson.objects.filter(course=lessons).count()

    def get_owner_email(self, obj):
        """Вывод информации об отсутствии владельца."""

        return obj.owner.email if obj.owner else "Владелец отсутствует"

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "description",
            "count_lessons",
            "lessons",
            "owner_email",
        )
