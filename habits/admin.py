from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "place",
        "time",
        "action",
        "is_pleasant",
        "related_habit",
        "periodicity",
        "reward",
        "execution_time",
        "is_public",
    )
    list_filter = ("user", "place", "time", "is_pleasant", "is_public")
    search_fields = (
        "place",
        "action",
    )
