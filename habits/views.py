from rest_framework import permissions
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)

from habits.models import Habit
from habits.paginators import HabitPagination
from habits.serializers import HabitSerializer
from users.permissions import IsOwner


class PublicHabitListAPIView(ListAPIView):
    """
    GET: список всех публичных привычек (без авторизации, только чтение).
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.AllowAny]  # Доступ без входа

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)


class UserHabitListAPIView(ListAPIView):
    """
    GET: список привычек текущего пользователя (только свои).
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class UserHabitCreateAPIView(CreateAPIView):
    """
    POST: создание привычки (автоматически привязывается к request.user).
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserHabitRetrieveAPIView(RetrieveAPIView):
    """
    GET: детальная информация о привычке.
    Доступ только для владельца.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class UserHabitUpdateAPIView(UpdateAPIView):
    """
    PUT/PATCH: редактирование привычки.
    Доступ только для владельца.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class UserHabitDestroyAPIView(DestroyAPIView):
    """
    DELETE: удаление привычки.
    Доступ только для владельца.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)
