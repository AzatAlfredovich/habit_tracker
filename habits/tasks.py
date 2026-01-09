import logging

from celery import shared_task
from django.utils import timezone

from .models import Habit, User
from .services import (format_reminder_message, is_habit_due,
                       send_habit_tg_notification)

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def send_habit_reminders(self):
    """
    Задача отправляет напоминания о привычках в Telegram.
    Уведомления отправляются, если текущее время совпадает с habit.time по минутам (секунды не учитываются).
    Предполагается, что tg_chat_id обязателен для всех пользователей.
    """
    try:
        # Получаем текущее время с учётом часового пояса
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        logger.info("Запуск задачи. Текущее время: %s", current_time)

        # Получаем всех пользователей
        users = User.objects.all()
        logger.info("Всего пользователей: %d", users.count())

        total_sent = 0
        total_failed = 0

        for user in users:
            try:
                logger.info(
                    "Обработка пользователя ID=%d, chat_id=%s", user.id, user.tg_chat_id
                )

                # Получаем все привычки пользователя
                habits = Habit.objects.filter(user=user)
                logger.info("У пользователя %d привычек: %d", user.id, habits.count())

                for habit in habits:
                    try:
                        habit_time = habit.time

                        # Проверка: совпадают ли часы и минуты (секунды игнорируем)
                        if (
                            current_time.hour != habit_time.hour
                            or current_time.minute != habit_time.minute
                        ):
                            logger.info(
                                "Привычка ID=%d: время не совпадает (ожидается в %02d:%02d, сейчас %02d:%02d)",
                                habit.id,
                                habit_time.hour,
                                habit_time.minute,
                                current_time.hour,
                                current_time.minute,
                            )
                            continue

                        # Проверка периодичности
                        if not is_habit_due(habit):
                            logger.info(
                                f"Привычка ID=%d: не актуальна сегодня (период: {habit.periodicity})",
                                habit.id,
                            )
                            continue  # корректно пропускаем, счётчики не трогаем

                        # Подготовка сообщения
                        try:
                            message = format_reminder_message(habit)
                        except Exception as e:
                            logger.error(
                                "Ошибка формирования сообщения для привычки ID=%d: %s",
                                habit.id,
                                str(e),
                            )
                            total_failed += 1
                            continue

                        # Отправка сообщения
                        try:
                            success = send_habit_tg_notification(
                                user.tg_chat_id, message
                            )
                            logger.info(
                                "Результат отправки для привычки %d: %r (тип: %s)",
                                habit.id,
                                success,
                                type(success),
                            )
                            if success:
                                total_sent += 1
                                logger.info(
                                    "Успешно отправлено для привычки ID=%d (пользователь ID=%d)",
                                    habit.id,
                                    user.id,
                                )
                            else:
                                total_failed += 1
                                logger.warning(
                                    "Отправка не удалась для привычки ID=%d (пользователь ID=%d) — API вернул False",
                                    habit.id,
                                    user.id,
                                )
                        except Exception as e:
                            total_failed += 1
                            logger.exception(
                                "Критическая ошибка при отправке для привычки ID=%d (пользователь ID=%d): %s",
                                habit.id,
                                user.id,
                                str(e),
                            )

                    except Exception as e:
                        total_failed += 1
                        logger.exception(
                            "Неожиданная ошибка при обработке привычки ID=%d (пользователь ID=%d): %s",
                            habit.id,
                            user.id,
                            str(e),
                        )

            except Exception as e:
                total_failed += 1
                logger.exception(
                    "Ошибка при обработке пользователя ID=%d: %s", user.id, str(e)
                )

        logger.info("Завершено. Отправлено: %d, ошибок: %d", total_sent, total_failed)
        return {"sent": total_sent, "failed": total_failed}

    except Exception as e:
        logger.exception("Критическая ошибка в send_habit_reminders: %s", str(e))
        return {"sent": 0, "failed": 1, "error": str(e)}
