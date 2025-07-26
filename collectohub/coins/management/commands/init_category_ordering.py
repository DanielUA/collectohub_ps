from django.core.management.base import BaseCommand
from coins.models import CoinCategory


class Command(BaseCommand):
    help = 'Ініціалізує значення ordering для всіх категорій монет'

    def handle(self, *args, **options):
        categories = CoinCategory.objects.all().order_by('id')
        
        for index, category in enumerate(categories, 1):
            if category.ordering == 0:  # Якщо ordering не встановлено
                category.ordering = index
                category.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Категорія "{category.name}" отримала ordering = {index}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Категорія "{category.name}" вже має ordering = {category.ordering}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Ініціалізація завершена. Оброблено {categories.count()} категорій.'
            )
        ) 