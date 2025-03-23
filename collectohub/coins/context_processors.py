from .models import *


def statistics_processor(request):
    return {
        'num_coins': Coin.objects.filter(status='a').count()
    }