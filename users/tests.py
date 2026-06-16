from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UsersTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(email='user1@test.pro')
        self.user1.set_password('12345')
        self.user1.save()
        self.user2 = User.objects.create(email='user2@test.pro')
        self.user2.set_password('12345')
        self.user2.save()

    def test_create_user(self):
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
        # self.assertEqual(response.data['email'], self.user1.email)
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
