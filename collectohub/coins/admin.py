from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_pic']

@admin.register(Continent)
class ContinentsAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Country)
class CountriesAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'material',
        'box',
        'circulation',
        'owner',
        'status',
        'tracking_number',
        ]
    list_filter = [
        'status',
    ]
    search_fields = [
        'denomination',
    ]

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'recipient', 'is_read', 'created']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(MultiOffer)
class MultiOfferAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(UserSurvey)
class UserSurveyAdmin(admin.ModelAdmin):
    list_display = ['user', 'created']

@admin.register(PageSeo)
class PageSeoAdmin(admin.ModelAdmin):
    list_display = ['url', 'title']
    search_fields = ['url', 'title', 'description']

@admin.register(GlobalScript)
class GlobalScriptAdmin(admin.ModelAdmin):
    list_display = ['name', 'position']
    search_fields = ['name', 'position']
    