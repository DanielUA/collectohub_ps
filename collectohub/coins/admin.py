from django.contrib import admin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import path
from .models import *
from .widgets import CategoryFilteredSelectMultiple



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_pic']
    filter_horizontal = ['badges']
    list_filter = ['badges']

@admin.register(Continent)
class ContinentsAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Country)
class CountriesAdmin(admin.ModelAdmin):
    list_display = ['name']
    
@admin.register(Topic)
class TopicsAdmin(admin.ModelAdmin):
    list_display = ['name']
    
@admin.register(TypeObject)
class TypeObjectsAdmin(admin.ModelAdmin):
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
        'material',
    ]
    search_fields = [
        'denomination',
        'category__name',
        'country__name',
    ]
    filter_horizontal = ['category']
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Використовуємо кастомний віджет для поля category"""
        if db_field.name == 'category':
            kwargs['widget'] = CategoryFilteredSelectMultiple(
                verbose_name="Категорії",
                is_stacked=False
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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
    
@admin.register(CoinCategory)
class CoinCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'get_countries', 'get_continents']
    search_fields = ['name', 'parent__name', 'countries__name', 'continents__name']
    list_filter = ['parent', 'countries', 'continents']
    filter_horizontal = ['countries', 'continents', 'type_objects']
    ordering = ['ordering']
    
    class Media:
        css = {
            'all': (
                'coins/css/category-ordering.css',
            )
        }
        js = (
            'coins/js/category-ordering.js',
        )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_filtered_categories_ajax/', 
                 self.admin_site.admin_view(self.get_filtered_categories_ajax), 
                 name='get_filtered_categories_ajax'),
            path('update_ordering/', 
                 self.admin_site.admin_view(self.update_ordering), 
                 name='update_ordering'),
        ]
        return custom_urls + urls
    
    @method_decorator(csrf_exempt)
    def get_filtered_categories_ajax(self, request):
        """AJAX endpoint для отримання відфільтрованих категорій"""
        country_id = request.GET.get('country_id')
        continent_id = request.GET.get('continent_id')
        
        queryset = CoinCategory.objects.all()
        
        if country_id:
            queryset = queryset.filter(countries__id=country_id)
        
        if continent_id:
            queryset = queryset.filter(continents__id=continent_id)
        
        categories = []
        for category in queryset.distinct():
            categories.append({
                'id': category.id,
                'name': str(category)
            })
        
        return JsonResponse({'categories': categories})
    
    @method_decorator(csrf_exempt)
    def update_ordering(self, request):
        """AJAX endpoint для оновлення порядку категорій"""
        if request.method == 'POST':
            try:
                import json
                data = request.POST
                updates_json = data.get('updates')
                
                if updates_json:
                    updates = json.loads(updates_json)
                    
                    for update in updates:
                        category_id = update.get('category_id')
                        new_ordering = update.get('ordering')
                        
                        if category_id and new_ordering is not None:
                            try:
                                category = CoinCategory.objects.get(id=category_id)
                                category.ordering = int(new_ordering)
                                category.save()
                            except CoinCategory.DoesNotExist:
                                continue
                    
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Missing updates data'})
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    def get_countries(self, obj):
        return ", ".join([country.name for country in obj.countries.all()[:3]])
    get_countries.short_description = 'Країни'
    
    def get_continents(self, obj):
        return ", ".join([continent.name for continent in obj.continents.all()[:3]])
    get_continents.short_description = 'Континенти'
    

    
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name', 'description']
    readonly_fields = ['created']
    list_editable = ['order', 'is_active']
    