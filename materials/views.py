from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, Lesson, Subscription
from materials.permissions import IsModerator, IsOwner

from .paginators import CourseLessonPagination
from .serializers import CourseSerializer, LessonSerializer
from .tasks import (
    send_information_about_add_course,
    send_information_about_add_lesson,
    send_information_about_update_course,
    send_information_about_update_lesson,
)


class CourseViewSet(ModelViewSet):
    """Класс работы с курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = CourseLessonPagination

    def perform_create(self, serializer):
        """Автоматически определяем владельца при создании."""

        course = serializer.save()
        course.owner = self.request.user
        course.save()
        send_information_about_add_course.delay(course.owner.email, course.name)

    def get_permissions(self):
        """Фильтруем действия создания, просмотр, редактирование, удаление
        либо по группе "moderators", либо по владельцу."""

        if self.action == "create":
            self.permission_classes = (~IsModerator,)

        elif self.action in (
            "retrieve",
            "update",
            "partial_update",
        ):
            self.permission_classes = (IsModerator | IsOwner,)

        elif self.action == "destroy":
            self.permission_classes = (IsOwner,)

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Фильтруем вывод списка либо по группе "moderators", либо по владельцу.
        Добавлена защита от ошибки построения схемы Swagger."""

        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()

        if not self.request.user.is_authenticated:
            return Course.objects.none()

        if self.request.user.groups.filter(name="moderators").exists():
            return Course.objects.all()

        return Course.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        """Отправка письма об изменении курса."""
        course = serializer.save()

        if self.action in ["update", "partial_update"]:
            send_information_about_update_course.delay(course.owner.email, course.name)


class LessonListAPIView(ListAPIView):
    """Класс вывода списка уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CourseLessonPagination

    def get_queryset(self):
        """Фильтруем вывод списка либо по группе "moderators", либо по владельцу"""

        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=self.request.user)


class LessonCreateAPIView(CreateAPIView):
    """Класс создания урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        """Автоматически определяем владельца при создании.
        Отправка письма о создании урока."""

        instance = serializer.save(owner=self.request.user)

        user = self.request.user
        course_name = instance.course.name if instance.course else None
        if user.email:
            send_information_about_add_lesson.delay(user.email, instance.name, course_name)


class LessonRetrieveAPIView(RetrieveAPIView):
    """Класс просмотра урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonUpdateAPIView(UpdateAPIView):
    """Класс редактирования урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

    def perform_update(self, serializer):
        """Отправка письма при изменении урока"""
        instance = serializer.save()
        user = instance.owner
        course_name = instance.course.name if instance.course else None

        send_information_about_update_lesson.delay(user.email, instance.name, course_name)


class LessonDestroyAPIView(DestroyAPIView):
    """Класс удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class SubscriptionAPIView(APIView):
    """Класс представления подписки."""

    def post(self, request, pk):
        user = request.user
        course = get_object_or_404(Course, pk=pk)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'

        return Response({'message': message})
