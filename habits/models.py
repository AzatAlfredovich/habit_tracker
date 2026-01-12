from django.db import models
from rest_framework.exceptions import ValidationError

from habits.validators import (validate_execution_time, validate_periodicity,
                               validate_pleasant_habit_restrictions,
                               validate_related_habit_is_pleasant)
from users.models import User


class Habit(models.Model):
    # Пользователь — создатель привычки
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )

    # Место выполнения привычки
    place = models.CharField(max_length=200, verbose_name="Место")

    # Время выполнения привычки (например, "18:00")
    time = models.TimeField(verbose_name="Время")

    # Действие — суть привычки
    action = models.TextField(verbose_name="Действие")

    # Признак "приятна ли привычка?"
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")

    # Связанная привычка - приятная альтернатива вознаграждению
    # (указывается для полезных привычек как дополнение следом за ней)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_habits",
        verbose_name="Связанная привычка",
    )

    # Периодичность в днях (по умолчанию — ежедневно, т.е. 1 день)
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность (в днях)",
        validators=[validate_periodicity],
    )

    # Вознаграждение за выполнение действия
    reward = models.TextField(blank=True, null=True, verbose_name="Вознаграждение")

    # Время на выполнение(в секундах)
    execution_time = models.PositiveIntegerField(
        verbose_name="Время на выполнение",
        validators=[validate_execution_time],
    )

    # Признак публичности "Публичная ли привычка?"
    is_public = models.BooleanField(default=False, verbose_name="Публичная привычка")

    # Дата создания (автоматически)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Привычка '{self.action}'"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["created_at"]

    def clean(self):
        # 1. Запрет на одновременное указание reward и related_habit
        if self.reward and self.related_habit:
            raise ValidationError(
                {
                    "reward": (
                        "Нельзя одновременно указать вознаграждение и связанную привычку. "
                        "Выберите только одно."
                    ),
                    "related_habit": (
                        "Нельзя одновременно указать вознаграждение и связанную привычку. "
                        "Выберите только одно."
                    ),
                }
            )

        # 2. Проверка, что связанная привычка — приятная
        validate_related_habit_is_pleasant(self)

        # 3. Проверка ограничений для приятных привычек
        validate_pleasant_habit_restrictions(self)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
