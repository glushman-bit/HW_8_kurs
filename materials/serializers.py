from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    """ Сериализатор уроков """
    class Meta:
        model = Lesson
        fields = ("id", "name", "description",)


class CourseSerializer(ModelSerializer):
    """ Сериализатор курсов """
    count_lessons = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons(self, lessons):
        """ Подсчет количества уроков на курсе """
        return Lesson.objects.filter(course=lessons).count()

    class Meta:
        model = Course
        fields = ("id", "name", "description", "count_lessons", "lessons")
