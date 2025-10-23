import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Waits until the database is ready for connections."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for the database to be ready...")
        for attempt in range(60):  # max 60 seconds
            try:
                conn = connections["default"]
                conn.cursor()
                self.stdout.write(self.style.SUCCESS("Database is ready."))
                return
            except OperationalError:
                time.sleep(1)

        raise OperationalError("Failed to connect to the database within the timeout period.")
