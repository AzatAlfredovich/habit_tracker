from django.db import models
from django.contrib.auth.models import User


class Habit(models.Model):
    # Пользователь — создатель привычки
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )

    # Место выполнения привычки
    place = models.CharField(
        max_length=200,
        verbose_name='Место'
    )

    # Время выполнения привычки (например, "18:00")
    time = models.TimeField(
        verbose_name='Время'
    )

    # Действие — суть привычки
    action = models.TextField(
        verbose_name='Действие'
    )

    # Признак "приятна ли привычка?"
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка'
    )

    # Связанная привычка - приятная альтернатива вознаграждению
    # (указывается для полезных привычек как дополнение следом за ней)
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_habits',
        verbose_name='Связанная привычка'
    )

    # Периодичность в днях (по умолчанию — ежедневно, т.е. 1 день)
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (в днях)'
    )

    # Вознаграждение за выполнение действия
    reward = models.TextField(
        blank=True,
        null=True,
        verbose_name='Вознаграждение'
    )

    # Время на выполнение
    execution_time = models.PositiveIntegerField(
        verbose_name='Время на выполнение'
    )

    # Признак публичности "Публичная ли привычка?"
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичная привычка'
    )

    # Дата создания (автоматически)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f"Привычка '{self.action}'"


    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['created_at']