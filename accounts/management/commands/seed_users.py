from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = "Test uchun admin va user yaratadi"

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username="admin").exists():
            CustomUser.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin12345",
                role=CustomUser.Role.ADMIN,
            )
        if not CustomUser.objects.filter(username="user").exists():
            CustomUser.objects.create_user(
                username="user",
                email="user@example.com",
                password="user12345",
                role=CustomUser.Role.USER,
            )
        self.stdout.write("Foydalanuvchilar tayyor")