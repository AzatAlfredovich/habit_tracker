from django.core.exceptions import ValidationError


def validate_execution_time(value):
    """Время выполнения не должно превышать 120 секунд."""
    if value > 120:
        raise ValidationError("Время на выполнение не может превышать 120 секунд.")


def validate_periodicity(value):
    """Периодичность должна быть от 1 до 7 дней."""
    if not (1 <= value <= 7):
        raise ValidationError(
            "Периодичность должна быть от 1 до 7 дней (включительно)."
        )


def validate_related_habit_is_pleasant(instance):
    """Связанная привычка должна быть приятной."""
    if instance.related_habit and not instance.related_habit.is_pleasant:
        raise ValidationError(
            {
                "related_habit": 'Связанная привычка должна иметь признак "приятная привычка".'
            }
        )


def validate_pleasant_habit_restrictions(instance):
    """
    Для приятной привычки:
    - не может быть вознаграждения (reward);
    - не может быть связанной привычки (related_habit).
    """
    if instance.is_pleasant:
        if instance.reward:
            raise ValidationError(
                {"reward": "Приятная привычка не может иметь вознаграждения."}
            )
        if instance.related_habit:
            raise ValidationError(
                {
                    "related_habit": "Приятная привычка не может иметь связанной привычки."
                }
            )
