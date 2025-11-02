import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Ensure superuser exists (idempotent)."

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@gmail.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Admin!234567")

        u, _ = User.objects.get_or_create(username=username, defaults={"email": email})
        u.is_staff = True
        u.is_superuser = True
        u.set_password(password)
        u.save()
        self.stdout.write(self.style.SUCCESS(
            f"OK: {u.username} staff={u.is_staff} superuser={u.is_superuser}"
        ))
