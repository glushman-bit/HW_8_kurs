from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    """ Сериализатор курсов """
    count_lessons = SerializerMethodField()

    def get_count_lessons(self, lessons):
        """ Подсчет количества уроков на курсе """
        return Lesson.objects.filter(course=lessons).count()

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(ModelSerializer):
    """ Сериализатор уроков """
    class Meta:
        model = Lesson
        fields = "__all__"
