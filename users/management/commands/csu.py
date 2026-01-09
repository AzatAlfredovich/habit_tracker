from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(email="admin@mail.ru")
        user.set_password("admin0000")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
