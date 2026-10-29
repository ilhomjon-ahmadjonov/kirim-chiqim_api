from django.core.management.base import BaseCommand
from transactions.rates import update_rates_from_cbu


class Command(BaseCommand):
    help = "Markaziy bank kurslarini yuklaydi"

    def handle(self, *args, **options):
        updated = update_rates_from_cbu()
        self.stdout.write(f"Kurslar yangilandi: {updated}")