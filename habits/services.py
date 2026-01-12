import logging

import requests
from django.utils import timezone

from config.settings import TELEGRAM_TOKEN, TELEGRAM_URL

logger = logging.getLogger(__name__)


def send_habit_tg_notification(tg_chat_id, message):
    """
    Функция отправки сообщения в Telegram
    """
    params = {
        "text": message,
        "chat_id": tg_chat_id,
    }

    try:
        response = requests.get(
            f"{TELEGRAM_URL}{TELEGRAM_TOKEN}/sendMessage", params=params, timeout=10
        )

        # Проверяем успешный HTTP-статус и ответ Telegram
        if response.status_code == 200:
            result = response.json()
            if result.get("ok") is True:
                return True  # Успешная отправка
            else:
                return False  # Ошибка от Telegram API
        else:
            return False  # HTTP-ошибка
    except (requests.exceptions.RequestException, ValueError):
        return False  # Любая ошибка (таймаут, исключение и т.п.)


def format_reminder_message(habit):
    """
    Формирует текст напоминания о привычке для Telegram
    """
    message = (
        "⏰ Напоминание о привычке!\n\n"
        f"Действие: {habit.action}\n"
        f"Место: {habit.place}\n"
        f"Время: {habit.time.strftime('%H:%M')}\n"
        f"Длительность: {habit.execution_time} сек\n"
    )

    if habit.reward:
        message += f"Вознаграждение: {habit.reward}\n"

    elif habit.related_habit:
        message += f"Связанная привычка: {habit.related_habit.action}\n"

    message += "\nУдачи в выполнении!"
    return message


def is_habit_due(habit) -> bool:
    """
    Проверяет, нужно ли выполнять привычку сегодня, исходя из периодичности.
    Учитывает часовые пояса и дату создания.
    """
    today = timezone.now().date()
    start_date = habit.created_at.date()

    # Защита от некорректных дат
    if start_date > today:
        logger.warning(
            "Дата создания привычки (%s) позже текущей даты (%s)", start_date, today
        )
        return False

    total_days = (today - start_date).days

    # Если периодичность = 1 — выполняем каждый день
    if habit.periodicity == 1:
        return True

    # Для периодичности > 1: проверяем кратность
    return total_days % habit.periodicity == 0
