from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    """Сериализатор уроков"""

    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "name",
            "description",
            "owner_email",
        )


class CourseSerializer(ModelSerializer):
    """Сериализатор курсов"""

    count_lessons = SerializerMethodField()
    owner_email = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons(self, lessons):
        """Подсчет количества уроков на курсе"""
        return Lesson.objects.filter(course=lessons).count()

    def get_owner_email(self, obj):
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
