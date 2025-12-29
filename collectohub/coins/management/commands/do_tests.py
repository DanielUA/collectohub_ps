from django.core.management.base import BaseCommand
from coins.models import Coin, CoinCategory


class Command(BaseCommand):
    help = 'Ініціалізує значення ordering для всіх категорій монет'

    def handle(self, *args, **options):
        coins = Coin.objects.filter(type_object=None).update(type_object=6)