from unittest.mock import MagicMock, patch

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

    def setup_stripe_mocks(self):
        """Подготовка моков Stripe."""

        self.product_patcher = patch("users.views.create_stripe_product")
        self.price_patcher = patch("users.views.create_stripe_price")
        self.session_patcher = patch("users.views.create_stripe_session")
        self.retrieve_patcher = patch("users.services.stripe.checkout.Session.retrieve")

        self.mock_product = self.product_patcher.start()
        self.mock_price = self.price_patcher.start()
        self.mock_session = self.session_patcher.start()
        self.mock_retrieve = self.retrieve_patcher.start()

        self.addCleanup(self.product_patcher.stop)
        self.addCleanup(self.price_patcher.stop)
        self.addCleanup(self.session_patcher.stop)
        self.addCleanup(self.retrieve_patcher.stop)

        fake_product = MagicMock()
        fake_product.id = 'prod_test'
        self.mock_product.return_value = fake_product

        fake_price = MagicMock()
        fake_price.id = 'price_test'
        self.mock_price.return_value = fake_price

        self.mock_session.return_value = (
            'cs_test_a1wEX9mj',
            'https://stripe.com',
        )

        fake_session = MagicMock()
        fake_session.payment_status = 'paid'
        self.mock_retrieve.return_value = fake_session

    def setUp(self):

        self.setup_stripe_mocks()

        self.user = User.objects.create(email='test_test@sky.pro')
        self.course = Course.objects.create(name='Course_1', description='desc_Course_1', owner=self.user)
        self.lesson = Lesson.objects.create(name='Lesson_1', course=self.course)
        # Платеж с сессией (для успешных тестов)
        self.payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=10000,
            session_id='cs_test_a1wEX9mj',
        )
        # Платеж без сессии (для проверки ошибок)
        self.payment_1 = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=10000,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_payment_course(self):
        """Тест создания платежа за курс."""

        url = reverse('users:payment-create')
        data = {
            'amount': 10000,
            'paid_course': self.course.pk,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('date_payment', response.data)
        self.assertEqual(response.data.get('session_id'), 'cs_test_a1wEX9mj')
        self.assertEqual(response.data.get('link'), 'https://stripe.com')

    def test_create_payment_lesson(self):
        """Тест создания платежа за урок."""

        url = reverse('users:payment-create')
        data = {
            'amount': 10000,
            'paid_course': self.lesson.pk,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('date_payment', response.data)
        self.assertEqual(response.data.get('session_id'), 'cs_test_a1wEX9mj')
        self.assertEqual(response.data.get('link'), 'https://stripe.com')

    def test_false_payment_missing_fields(self):
        """Тест ошибки: не передан ни курс, ни урок."""
        url = reverse('users:payment-create')
        data = {'amount': 10000}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Нужно указать оплачиваемый курс или урок.')

    #
    def test_false_payment_fields(self):
        """Тест ошибки: переданы одновременно и курс, и урок."""
        url = reverse('users:payment-create')
        course_2 = Course.objects.create(name='Course_2', description='desc_Course_2', owner=self.user)
        lesson_2 = Lesson.objects.create(name='Lesson_2', course=course_2)
        data = {
            'amount': 10000,
            'paid_course': course_2.pk,
            'paid_lesson': lesson_2.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Можно оплатить либо курс, либо урок.')

    def test_payment_status(self):
        """Тест получения статуса платежа."""

        url = reverse('users:payment-retrieve', args=(self.payment.pk,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'paid')

    def test_payment_session_error(self):
        """Тест ошибку, если у платежа нет session_id."""

        url = reverse('users:payment-retrieve', args=(self.payment_1.pk,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], 'Для данного платежа отсутствует session_id.')

    def test_payment_amount_error(self):
        """Тест на не соответствие цены."""

        url = reverse('users:payment-create')
        data = {
            "paid_course": 1,
            "amount": 100,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
        self.assertEqual(response.data['amount'][0], 'Цена не может быть менее 10000 копеек.')
