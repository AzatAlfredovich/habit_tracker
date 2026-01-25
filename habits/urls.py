from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from habits.apps import HabitsConfig
from habits.views import (PublicHabitListAPIView, UserHabitCreateAPIView,
                          UserHabitDestroyAPIView, UserHabitListAPIView,
                          UserHabitRetrieveAPIView, UserHabitUpdateAPIView)

app_name = HabitsConfig.name

urlpatterns = [
    path("public/", PublicHabitListAPIView.as_view(), name="public_habits_list"),
    path("my/", UserHabitListAPIView.as_view(), name="my_habits_list"),
    path("<int:pk>/", UserHabitRetrieveAPIView.as_view(), name="habits_retrieve"),
    path("create/", UserHabitCreateAPIView.as_view(), name="habits_create"),
    path("<int:pk>/update/", UserHabitUpdateAPIView.as_view(), name="habits_update"),
    path(
        "<int:pk>/delete/",
        UserHabitDestroyAPIView.as_view(),
        name="habits_delete",
    ),
]
