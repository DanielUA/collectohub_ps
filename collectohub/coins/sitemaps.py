# coins/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Coin, Continent, Country, User  # імпортуй тільки потрібне

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['coins:home_page', 'coins:index', 'coins:about-me']

    def location(self, item):
        return reverse(item)


class CoinSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return Coin.objects.filter(status='a')  # або інший фільтр для публічних монет

    def location(self, obj):
        return reverse('coins:coin-detail', kwargs={'pk': obj.pk})


class ContinentSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Continent.objects.all()

    def location(self, obj):
        return reverse('coins:continent-detail', kwargs={'pk': obj.pk})


class CountrySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Country.objects.all()

    def location(self, obj):
        return reverse('coins:country-detail', kwargs={'pk': obj.pk})
