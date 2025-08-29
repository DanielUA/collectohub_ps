from django.core.management.base import BaseCommand
from coins.models import Coin, CoinCategory


class Command(BaseCommand):
    help = 'Ініціалізує значення ordering для всіх категорій монет'

    def handle(self, *args, **options):
        coins = Coin.objects.all()
        for coin in coins:
            print(coin.pk)
            # Правильний спосіб очищення ImageField
            # if coin.qr_code:
            #     coin.qr_code.delete(save=False)  # Видаляє файл з диску
            coin.qr_code = None  # Очищає поле в базі даних
            coin.save()