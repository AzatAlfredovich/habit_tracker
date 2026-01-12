
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitAPITest(APITestCase):
    def setUp(self):
        # Создаём пользователя и авторизуем клиента
        self.user = User.objects.create(
            email="newuser@example.com",
            tg_chat_id="55555",
            phone_number="+79991234567",
            password="securepass123",
        )
        self.client.force_authenticate(user=self.user)
        Habit.objects.all().delete()

        # URL на основе ваших маршрутов
        self.public_list_url = reverse("habits:public_habits_list")
        self.my_list_url = reverse("habits:my_habits_list")
        self.create_url = reverse("habits:habits_create")
        self.retrieve_url = lambda pk: reverse(
            "habits:habits_retrieve", kwargs={"pk": pk}
        )
        self.update_url = lambda pk: reverse("habits:habits_update", kwargs={"pk": pk})
        self.delete_url = lambda pk: reverse("habits:habits_delete", kwargs={"pk": pk})

    # Создание привычки
    def test_create_habit_success(self):
        """Успешное создание привычки через /create/."""
        data = {
            "place": "Дом",
            "time": "18:00:00",
            "action": "Читать книгу",
            "execution_time": 60,
            "is_pleasant": False,
        }
        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(response.data["action"], "Читать книгу")
        self.assertEqual(
            response.data["user"], self.user.id
        )  # user должен подставиться автоматически

    def test_create_habit_missing_required_fields(self):
        """Ошибка при отсутствии обязательных полей."""
        data = {"action": "Читать"}  # Нет place, time, execution_time
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ["place", "time", "execution_time"]:
            self.assertIn(field, response.data)

    # Получение списка привычек
    def test_my_habits_list(self):
        Habit.objects.create(
            user=self.user,
            place="Дом",
            time="18:00",
            action="Читать",
            execution_time=60,
        )
        response = self.client.get(self.my_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # Общее число записей
        self.assertEqual(len(response.data["results"]), 1)  # Длина списка results
        self.assertEqual(response.data["results"][0]["action"], "Читать")

    def test_public_habits_list(self):
        Habit.objects.create(
            user=self.user,
            place="Парк",
            time="09:00",
            action="Бегать",
            execution_time=120,
            is_public=True,
        )
        Habit.objects.create(  # Непубличная — не должна попасть
            user=self.user,
            place="Офис",
            time="12:00",
            action="Работать",
            execution_time=3600,
            is_public=False,
        )

        response = self.client.get(self.public_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Бегать")

    # Тест деталей привычки
    def test_retrieve_habit_success(self):
        """Получение конкретной привычки через /<pk>/."""
        habit = Habit.objects.create(
            user=self.user,
            place="Парк",
            time="09:00",
            action="Бегать",
            execution_time=120,
        )
        response = self.client.get(self.retrieve_url(habit.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["place"], "Парк")
        self.assertEqual(response.data["user"], self.user.id)

    def test_retrieve_other_user_habit(self):
        """Попытка получить привычку другого пользователя."""
        other_user = User.objects.create(email="other@example.com", password="pass")
        habit = Habit.objects.create(
            user=other_user,
            place="Офис",
            time="10:00",
            action="Работать",
            execution_time=3600,
        )

        response = self.client.get(self.retrieve_url(habit.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Тест обновления привычки
    def test_update_habit_success(self):
        """Успешное обновление привычки через /<pk>/update/."""
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="18:00",
            action="Читать",
            execution_time=60,
        )
        data = {
            "place": "Библиотека",
            "time": "20:00:00",
            "action": "Учить Python",
            "execution_time": 90,
        }
        response = self.client.put(self.update_url(habit.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.place, "Библиотека")
        self.assertEqual(habit.action, "Учить Python")

    def test_update_unauthorized_habit(self):
        """Попытка обновить привычку другого пользователя."""
        other_user = User.objects.create(email="other@example.com", password="pass")
        habit = Habit.objects.create(
            user=other_user,
            place="Офис",
            time="10:00",
            action="Работать",
            execution_time=3600,
        )

        data = {"place": "Кафе"}
        response = self.client.put(self.update_url(habit.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Тест удаления привычки
    def test_delete_habit_success(self):
        """Успешное удаление привычки через /<pk>/delete/."""
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="18:00",
            action="Читать",
            execution_time=60,
        )
        response = self.client.delete(self.delete_url(habit.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=habit.pk).exists())

    def test_delete_other_user_habit(self):
        """Попытка удалить привычку другого пользователя."""
        other_user = User.objects.create(email="other@example.com", password="pass")
        habit = Habit.objects.create(
            user=other_user,
            place="Офис",
            time="10:00",
            action="Работать",
            execution_time=3600,
        )

        response = self.client.delete(self.delete_url(habit.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Habit.objects.filter(pk=habit.pk).exists())

    def test_str_method(self):
        # Создаём экземпляр модели (тест строкового представления)
        habit = Habit(action="Делать зарядку")
        # Проверяем, что __str__ возвращает ожидаемую строку
        self.assertEqual(str(habit), "Привычка 'Делать зарядку'")

    def test_clean_raises_validation_error_when_both_reward_and_related_habit_set(self):
        other_user = User.objects.create(email="other@example.com", password="pass")

        related_habit = Habit.objects.create(
            user=other_user,
            action="Потянуть мышцы",
            time="08:00",
            execution_time=3600,
        )

        habit = Habit(
            user=other_user,
            action="Бегать утром",
            time="08:00",
            execution_time=3600,
            reward="Чашка кофе",
            related_habit=related_habit
        )

        expected_msg = (
            "Нельзя одновременно указать вознаграждение и связанную привычку. "
            "Выберите только одно."
        )

        # Ловим DRF-исключение
        with self.assertRaises(ValidationError) as context:
            habit.clean()  # или вызов сериализатора/вью

        # Получаем ошибки из .detail
        errors = context.exception.detail

        # Проверяем наличие полей в ошибках
        self.assertIn("reward", errors)
        self.assertIn("related_habit", errors)

        # В DRF errors["field"] — это список строк
        self.assertIn(expected_msg, errors["reward"])
        self.assertIn(expected_msg, errors["related_habit"])