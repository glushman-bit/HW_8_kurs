from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import Payment, User


class UsersTestCase(APITestCase):
    """TestCase для пользователей."""

    def setUp(self):
        self.user1 = User.objects.create(email='user1@test.pro')
        self.user1.set_password('12345')
        self.user1.save()
        self.user2 = User.objects.create(email='user2@test.pro')
        self.user2.set_password('12345')
        self.user2.save()

    def test_create_user(self):
        """Тест создания пользователя."""
        url = reverse('users:register')
        data = {
            'email': 'user3@test.pro',
            'password': '12345',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

        user = User.objects.first()
        self.assertEqual(user.email, 'user1@test.pro')
        self.assertEqual(user.check_password('12345'), True)

    def test_view_profile(self):
        """Тест просмотра своего профиля."""
        url = reverse('users:user-detail', args=(self.user1.pk,))

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], self.user1.phone)
        self.assertIn("pay_history", response.data)

    def test_update_own_profile(self):
        """Проверка изменения своего профиля."""
        url = reverse('users:user-detail', args=(self.user1.pk,))
        self.client.force_authenticate(user=self.user1)
        data = {'city': 'Moscow'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Получаем актуальные данные из БД
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.city, 'Moscow')

    def test_view_other_profile(self):
        """Просмотр чужого профиля."""
        url = reverse('users:user-detail', args=(self.user2.pk,))
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user2.email)
        # Не можем посмотреть
        self.assertNotIn('phone', response.data)
        self.assertNotIn("pay_history", response.data)
        # Можем посмотреть
        self.assertIn('avatar', response.data)
        self.assertIn('city', response.data)

    def test_update_other_profile(self):
        """Проверка запрета на изменение чужого профиля."""
        url = reverse('users:user-detail', args=(self.user2.pk,))
        self.client.force_authenticate(user=self.user1)
        data = {'city': 'Moscow'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.user2.city, 'Moscow')
        # Получаем актуальные данные из БД
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.city, None)


class PaymentTestCase(APITestCase):
    """TestCase для платежа."""

    def setUp(self):
        self.user = User.objects.create(email='test_test@sky.pro')
        self.course = Course.objects.create(name='Course_1', description='desc_Course_1', owner=self.user)
        self.lesson = Lesson.objects.create(name='Lesson_1', course=self.course)
        self.payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=100,
            session_id='cs_test_a1wEX9mjiG21VcLKHV2z2GmIQ2UGLc6BivjDHWsnmlkCCefGcC36iIXLX5',
        )
        self.payment_1 = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=100,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_payment(self):
        """Тест создания платежа."""
        url = reverse('users:payment-create')
        response = self.client.post(url, {'amount': self.payment.amount, 'paid_course': self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('date_payment', response.data)
        self.assertIn('session_id', response.data)
        self.assertIn('link', response.data)

        response = self.client.post(url, {'amount': self.payment.amount, 'paid_lesson': self.lesson.pk})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('date_payment', response.data)
        self.assertIn('session_id', response.data)
        self.assertIn('link', response.data)

    def test_false_payment(self):
        """Тест неверного платежа."""
        url = reverse('users:payment-create')

        course_1 = Course.objects.create(name='Course_2', description='desc_Course_1', owner=self.user)
        lesson_1 = Lesson.objects.create(name='Lesson_1', course=self.course)

        response = self.client.post(url, {'amount': self.payment.amount})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Нужно указать оплачиваемый курс или урок.')

        response = self.client.post(
            url, {'amount': self.payment.amount, 'paid_course': course_1.pk, 'paid_lesson': lesson_1.pk}
        )
        self.assertEqual(response.data['non_field_errors'][0], 'Можно оплатить либо курс, либо урок.')

    def test_payment_status(self):
        """Тест статуса платежа."""
        url = reverse('users:payment-retrieve', args=(self.payment.pk,))
        response = self.client.get(url, self.payment.status)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)

    def test_payment_session_error(self):
        """Тест на отсутствие сессии."""
        url = reverse('users:payment-retrieve', args=(self.payment_1.pk,))
        response = self.client.get(url, self.payment_1.status)
        print(response.text)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
