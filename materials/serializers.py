from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    """ Сериализатор уроков """
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    """ Сериализатор курсов """
    count_lessons = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons(self, lessons):
        """ Подсчет количества уроков на курсе """
        return Lesson.objects.filter(course=lessons).count()

    class Meta:
        model = Course
        fields = "__all__"
