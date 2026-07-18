from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from materials.validators import VideoUrlValidator
from users.models import User


class BaseTestCase(APITestCase):
    """Базовый класс тестов."""

    def setUp(self):
        self.user = User.objects.create(email='test_test@sky.pro')
        self.course = Course.objects.create(name='Course_1', description='desc_Course_1', owner=self.user)
        self.lesson = Lesson.objects.create(
            name='lesson_test',
            description='desc_lesson_test',
            course=self.course,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)


class LessonTestCase(BaseTestCase):
    """TestCase для урока."""

    def test_lesson_create(self):
        """Тест создания урока."""
        url = reverse('materials:lesson_create')
        data = {
            'name': self.lesson.name,
            'description': self.lesson.description,
            'course': self.course.id,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

        # Проверка корректность созданного урока
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.name, 'lesson_test')
        self.assertEqual(lesson.description, 'desc_lesson_test')
        self.assertEqual(lesson.course, self.course)
        self.assertEqual(lesson.owner, self.user)

    def test_lesson_retrieve(self):
        """Тест на вывод информации об уроке."""

        url = reverse('materials:lesson_detail', args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'lesson_test')
        self.assertEqual(response.data['description'], 'desc_lesson_test')
        self.assertEqual(response.data['course'], self.course.id)
        self.assertEqual(response.data['owner_email'], self.user.email)

    def test_lesson_update(self):
        """Тест на изменения в уроке."""

        data = {
            'name': 'lesson_test_2',
        }

        url = reverse('materials:lesson_update', args=[self.lesson.id])
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('name'), 'lesson_test_2')

    def test_lesson_delete(self):
        """Тест удаления урока."""
        url = reverse('materials:lesson_delete', args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        """Тест вывода списка уроков."""
        url = reverse('materials:lesson_list')
        response = self.client.get(url)
        data = response.json()

        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "course": self.course.pk,
                    "name": self.lesson.name,
                    "description": self.lesson.description,
                    "video_url": None,
                    "owner_email": self.user.email,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class CourseTestCase(BaseTestCase):
    """TestCase для курса."""

    def test_course_create(self):
        """Тест создания курса."""
        url = reverse('materials:course-list')
        data = {
            "name": self.course.name,
            "description": self.course.description,
            "owner_email": self.user.email,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

        # Проверка корректность созданного курса
        course = Course.objects.first()
        self.assertEqual(course.name, "Course_1")
        self.assertEqual(course.description, "desc_Course_1")
        self.assertEqual(course.owner, self.user)

    def test_course_retrieve(self):
        """Тест на вывод информации о курсе."""
        url = reverse('materials:course-detail', args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('name'), 'Course_1')
        self.assertEqual(data.get('description'), 'desc_Course_1')

    def test_course_update(self):
        """Тест на внесение изменения в курс."""
        url = reverse('materials:course-detail', args=(self.course.pk,))
        data = {
            "name": "test_course",
        }
        response = self.client.patch(url, data)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('name'), 'test_course')

    def test_course_delete(self):
        """Тест на удаление курса."""
        url = reverse('materials:course-detail', args=(self.course.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)

    def test_course_list(self):
        """Тест вывод списка курсов."""
        url = reverse('materials:course-list')
        response = self.client.get(url)
        data = response.json()
        print(data)
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": self.course.name,
                    "description": self.course.description,
                    "count_lessons": 1,
                    "lessons": [
                        {
                            "id": 1,
                            "course": self.course.id,
                            "name": self.lesson.name,
                            "description": self.lesson.description,
                            "video_url": None,
                            "owner_email": self.user.email,
                        }
                    ],
                    "owner_email": self.user.email,
                    "is_subscribed": False,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class SubscriptionTestCase(BaseTestCase):
    """TestCase для подписки."""

    def test_subscription_on_off(self):
        """Тест на создание и удаление подписки."""
        url = reverse('materials:course_subscribe', args=(self.course.pk,))
        # Проверка создания подписки
        response = self.client.post(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('message'), 'Подписка добавлена')
        self.assertEqual(Subscription.objects.count(), 1)

        # Проверка наличия подписки у пользователя
        subscription = Subscription.objects.first()
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.course, self.course)

        # Проверка удаления подписки
        response = self.client.post(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('message'), 'Подписка удалена')
        self.assertEqual(Subscription.objects.count(), 0)


class VideoUrlValidatorTestCase(SimpleTestCase):
    """Тестирование валидатора поля 'video_url'."""

    def setUp(self):
        self.validator = VideoUrlValidator()

    def test_valid_youtube_url(self):
        """Тест на валидную ссылку."""
        self.validator("https://youtube.com/watch?v=123")

    def test_invalid_url(self):
        """Тест на невалидную ссылку."""
        with self.assertRaises(ValidationError):
            self.validator("https://google.com")

    def test_empty_url(self):
        """Тест на пустую строку."""
        self.validator("")
