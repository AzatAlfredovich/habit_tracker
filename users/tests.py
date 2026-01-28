from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User
from users.permissions import IsOwner


class UserRegistrationAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse("users:register")  # URL для регистрации
        self.login_url = reverse("users:login")  # URL для логина

    def test_register_user_success(self):
        """Успешная регистрация пользователя."""
        data = {
            "email": "newuser@example.com",
            "tg_chat_id": "55555",
            "phone_number": "+79991234567",
            "password": "securepass123",
        }
        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        self.assertEqual(str(user), "newuser@example.com")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.tg_chat_id, "55555")
        # phone_number может быть None — проверяем, что сохранилось
        self.assertEqual(user.phone_number, "+79991234567")

    def test_register_missing_email(self):
        """Ошибка при отсутствии email."""
        data = {"tg_chat_id": "11111", "password": "securepass123"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_tg_chat_id(self):
        """Ошибка при пустом/None tg_chat_id."""
        # Пустая строка
        data_empty = {
            "email": "no_tg@example.com",
            "tg_chat_id": "",
            "password": "securepass123",
        }
        response_empty = self.client.post(self.register_url, data_empty, format="json")
        self.assertEqual(response_empty.status_code, status.HTTP_400_BAD_REQUEST)

        # None
        data_none = {
            "email": "none_tg@example.com",
            "tg_chat_id": None,
            "password": "securepass123",
        }
        response_none = self.client.post(self.register_url, data_none, format="json")
        self.assertEqual(response_none.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_unique(self):
        """Проверка уникальности email при регистрации."""
        # Создаём пользователя
        User.objects.create(email="unique@example.com", tg_chat_id="22222")

        # Пытаемся зарегистрировать с тем же email
        data = {
            "email": "unique@example.com",
            "tg_chat_id": "33333",
            "password": "securepass123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_credentials(self):
        """Ошибка при неверном email/пароле."""
        login_data = {"email": "wrong@example.com", "password": "wrongpass"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_optional_phone_number(self):
        """phone_number может быть пустым."""
        data = {
            "email": "optionalphone@example.com",
            "tg_chat_id": "66666",
            "password": "securepass123",
            # phone_number не передаём
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_admin_command(self):
        # Вызываем команду без перехвата вывода
        call_command('csu')

        # Проверяем, что пользователь создан
        self.assertTrue(
            User.objects.filter(email="admin@mail.ru").exists()
        )

        # Получаем пользователя
        user = User.objects.get(email="admin@mail.ru")

        # Проверяем ключевые атрибуты
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        # Убеждаемся, что пароль хеширован (не хранится в открытом виде)
        self.assertNotEqual(user.password, "admin0000")

        # Проверяем валидность пароля
        self.assertTrue(user.check_password("admin0000"))


class IsOwnerPermissionSimpleTest(APITestCase):
    def setUp(self):
        # Создаём двух пользователей
        self.owner = User.objects.create(email="owner@example.com", tg_chat_id="22222")
        self.other = User.objects.create(email="other@example.com", tg_chat_id="22233")

        # Создаём объект, принадлежащий owner
        self.obj = Habit.objects.create(
            user=self.owner,
            action="Бегать утром",
            time="08:00",
            execution_time=3600,
            reward="Чашка кофе",
        )

        # Инициализируем пермишен
        self.permission = IsOwner()

    def test_owner_returns_true(self):
        """Владелец получает True."""
        request = self.client.get("/").wsgi_request  # получаем сырой request
        request.user = self.owner

        result = self.permission.has_object_permission(request, None, self.obj)
        self.assertTrue(result)

    def test_other_user_returns_false(self):
        """Не владелец получает False."""
        request = self.client.get("/").wsgi_request
        request.user = self.other

        result = self.permission.has_object_permission(request, None, self.obj)
        self.assertFalse(result)
