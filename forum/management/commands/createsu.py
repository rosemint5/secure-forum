import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

class Command(BaseCommand):
    help = "Create a superuser from ENV if it doesn't exist."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("ADMIN_USERNAME") or os.getenv("DJANGO_SUPERUSER_USERNAME")
        email    = os.getenv("ADMIN_EMAIL")    or os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("ADMIN_PASSWORD") or os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                "Missing superuser ENV (username/email/password) – skipping."
            ))
            return

        try:
            validate_password(password)
        except ValidationError as e:
            for msg in e.messages:
                self.stdout.write(self.style.ERROR(f"Password invalid: {msg}"))
            return

        with transaction.atomic():
            user, created = User.objects.get_or_create(username=username, defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            })

            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
                self.stdout.write(self.style.SUCCESS(f"Superuser created: {username}"))
                return

            changed = False
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True

            user.set_password(password)
            changed = True

            if changed:
                user.email = email or user.email
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Superuser updated: {username}"))
            else:
                self.stdout.write("Superuser already exists – no changes.")
