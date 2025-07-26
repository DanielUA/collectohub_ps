from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from django.utils.safestring import mark_safe
from .models import Country, Continent, CoinCategory

class CategoryFilteredSelectMultiple(FilteredSelectMultiple):
    """
    Кастомний FilteredSelectMultiple з фільтрацією категорій по країні та континенту
    """
    
    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        super().__init__(verbose_name, is_stacked, attrs, choices)
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
    
    def render(self, name, value, attrs=None, renderer=None):
        """Рендеримо віджет з додатковими фільтрами"""
        # Отримуємо базовий HTML віджета
        output = super().render(name, value, attrs, renderer)
        
        # Додаємо фільтри перед віджетом
        filter_html = self._get_filter_html()
        
        # Додаємо JavaScript безпосередньо в HTML
        script_html = '''
        <script>
        // Чекаємо поки сторінка повністю завантажиться
        window.addEventListener('load', function() {
            console.log('Page fully loaded, initializing category filter widget');
            
            // Додаткова затримка для завантаження Django admin скриптів
            setTimeout(function() {
                if (typeof django !== 'undefined' && django.jQuery) {
                    var $ = django.jQuery;
                    console.log('jQuery found, initializing widget');
                    
                    var filterPanel = $('.category-filter-panel');
                    var categoryWidget = $('.filtered');
                    
                    console.log('Filter panel found:', filterPanel.length);
                    console.log('Category widget found:', categoryWidget.length);
                    
                    // Якщо не знайшли віджет, спробуємо інші селектори
                    if (!categoryWidget.length) {
                        categoryWidget = $('.selector');
                        console.log('Trying .selector selector:', categoryWidget.length);
                    }
                    
                    if (!categoryWidget.length) {
                        categoryWidget = $('[class*="filtered"]');
                        console.log('Trying [class*="filtered"] selector:', categoryWidget.length);
                    }
                    
                    if (!categoryWidget.length) {
                        // Спробуємо знайти віджет за структурою
                        categoryWidget = $('div:has(.selector-available):has(.selector-chosen)');
                        console.log('Trying div with selector-available and selector-chosen:', categoryWidget.length);
                    }
                    
                    if (!categoryWidget.length) {
                        // Спробуємо знайти будь-який div з двома select елементами
                        $('div').each(function() {
                            var div = $(this);
                            var selects = div.find('select');
                            if (selects.length >= 2) {
                                console.log('Found div with', selects.length, 'selects:', div.attr('class'));
                                categoryWidget = div;
                                return false; // break each loop
                            }
                        });
                        console.log('Found div with multiple selects:', categoryWidget.length);
                    }
                    
                    if (!filterPanel.length || !categoryWidget.length) {
                        console.log('Required elements not found');
                        console.log('Available elements on page:');
                        $('*').each(function() {
                            var className = $(this).attr('class');
                            if (className && (className.includes('filter') || className.includes('select') || className.includes('category') || className.includes('available') || className.includes('chosen'))) {
                                console.log('Found element with class:', className, 'tag:', this.tagName);
                            }
                        });
                        
                        // Додатково шукаємо всі select елементи
                        console.log('All select elements on page:');
                        $('select').each(function(index) {
                            var select = $(this);
                            console.log('Select', index, 'id:', select.attr('id'), 'class:', select.attr('class'), 'options:', select.find('option').length);
                        });
                        return;
                    }
                    
                    var countryFilter = $('#category_country_filter');
                    var continentFilter = $('#category_continent_filter');
                    var applyButton = $('#apply_category_filter');
                    var clearButton = $('#clear_category_filter');
                    
                    console.log('Filters found:', countryFilter.length, continentFilter.length);
                    console.log('Buttons found:', applyButton.length, clearButton.length);
                    
                    // Зберігаємо оригінальні опції
                    var originalOptions = {};
                    
                    // Знаходимо тільки select з доступними категоріями (лівий список)
                    var availableSelect = null;
                    var options = null;
                    
                    // Знаходимо select елемент за правильним селектором
                    availableSelect = $('select[name="category_old"]');
                    console.log('Found select with name="category_old":', availableSelect.length);
                    
                    if (availableSelect.length > 0) {
                        options = availableSelect.find('option');
                        console.log('Options found:', options.length);
                    }
                    

                    
                    // Зберігаємо оригінальні опції тільки якщо знайшли select
                    if (availableSelect && options) {
                        options.each(function() {
                            var option = $(this);
                            var value = option.val();
                            var text = option.text();
                            if (value) {
                                originalOptions[value] = {
                                    text: text,
                                    element: option.clone()
                                };
                            }
                        });
                        
                        console.log('Original options saved:', Object.keys(originalOptions).length);
                    } else {
                        console.log('No select element found for filtering');
                    }
                    
                    options.each(function() {
                        var option = $(this);
                        var value = option.val();
                        var text = option.text();
                        console.log('Option found:', value, text);
                        if (value) {
                            originalOptions[value] = {
                                text: text,
                                element: option.clone()
                            };
                        }
                    });
                    
                    console.log('Original options saved:', Object.keys(originalOptions).length);
                    
                    // Функція для фільтрації категорій
                    function filterCategories() {
                        if (!availableSelect) {
                            console.log('No available select found for filtering');
                            return;
                        }
                        
                        var countryId = countryFilter.val();
                        var continentId = continentFilter.val();
                        
                        console.log('Filtering by country:', countryId, 'continent:', continentId);
                        
                        // Показуємо індикатор завантаження
                        availableSelect.parent().addClass('loading');
                        
                        // Очищаємо поточний список
                        availableSelect.empty();
                        availableSelect.append('<option value="">---------</option>');
                        
                        // Якщо не вибрано фільтрів, показуємо всі категорії
                        if (!countryId && !continentId) {
                            $.each(originalOptions, function(value, option) {
                                availableSelect.append(option.element);
                            });
                            console.log('No filters selected, showing all categories');
                            availableSelect.parent().removeClass('loading');
                            return;
                        }
                        
                        // Відправляємо AJAX запит для отримання відфільтрованих категорій
                        $.ajax({
                            url: '/admin/coins/coincategory/get_filtered_categories_ajax/',
                            method: 'GET',
                            data: {
                                country_id: countryId,
                                continent_id: continentId,
                                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                            },
                            success: function(data) {
                                console.log('AJAX success:', data);
                                
                                // Додаємо відфільтровані категорії
                                $.each(data.categories, function(index, category) {
                                    availableSelect.append(
                                        $('<option></option>')
                                            .val(category.id)
                                            .text(category.name)
                                    );
                                });
                                
                                console.log('Filter applied, showing', data.categories.length, 'categories');
                                availableSelect.parent().removeClass('loading');
                            },
                            error: function(xhr, status, error) {
                                console.error('AJAX error:', status, error);
                                console.error('Response:', xhr.responseText);
                                
                                // У випадку помилки показуємо всі категорії
                                $.each(originalOptions, function(value, option) {
                                    availableSelect.append(option.element);
                                });
                                
                                console.log('Error occurred, showing all categories');
                                availableSelect.parent().removeClass('loading');
                            }
                        });
                    }
                    
                    // Функція для очищення фільтрів
                    function clearFilters() {
                        console.log('Clearing filters');
                        countryFilter.val('');
                        continentFilter.val('');
                        
                        // Відновлюємо оригінальні опції
                        availableSelect.empty();
                        availableSelect.append('<option value="">---------</option>');
                        $.each(originalOptions, function(value, option) {
                            availableSelect.append(option.element);
                        });
                        
                        console.log('Filters cleared, restored', Object.keys(originalOptions).length, 'categories');
                    }
                    
                    // Функція для оновлення originalOptions
                    function updateOriginalOptions() {
                        console.log('Updating original options...');
                        originalOptions = {};
                        
                        var currentOptions = availableSelect.find('option');
                        currentOptions.each(function() {
                            var option = $(this);
                            var value = option.val();
                            var text = option.text();
                            if (value) {
                                originalOptions[value] = {
                                    text: text,
                                    element: option.clone()
                                };
                            }
                        });
                        
                        console.log('Original options updated:', Object.keys(originalOptions).length);
                    }
                    
                    // Обробники подій для кнопок фільтрації
                    applyButton.on('click', function() {
                        console.log('Apply button clicked');
                        filterCategories();
                    });
                    
                    clearButton.on('click', function() {
                        console.log('Clear button clicked');
                        clearFilters();
                    });
                    
                    // Обробники подій для кнопок переміщення категорій
                    $('#id_category_add_all_link').on('click', function() {
                        console.log('Add all button clicked');
                        setTimeout(updateOriginalOptions, 100); // Затримка для оновлення DOM
                    });
                    
                    $('#id_category_add_link').on('click', function() {
                        console.log('Add button clicked');
                        setTimeout(updateOriginalOptions, 100);
                    });
                    
                    $('#id_category_remove_link').on('click', function() {
                        console.log('Remove button clicked');
                        setTimeout(updateOriginalOptions, 100);
                    });
                    
                    $('#id_category_remove_all_link').on('click', function() {
                        console.log('Remove all button clicked');
                        setTimeout(updateOriginalOptions, 100);
                    });
                    
                    console.log('Category filter widget initialization complete');
                } else {
                    console.log('jQuery not found, retrying...');
                    setTimeout(arguments.callee, 200);
                }
            }, 500);
        });
        </script>
        '''
        
        return mark_safe(filter_html + output + script_html)
    
    def _get_filter_html(self):
        """Генеруємо HTML для фільтрів"""
        countries = Country.objects.all().order_by('name')
        continents = Continent.objects.all().order_by('name')
        
        country_options = '<option value="">Всі країни</option>'
        for country in countries:
            country_options += f'<option value="{country.id}">{country.name}</option>'
        
        continent_options = '<option value="">Всі континенти</option>'
        for continent in continents:
            continent_options += f'<option value="{continent.id}">{continent.name}</option>'
        
        return f'''
        <style>
        .category-filter-panel {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .category-filter-panel > div {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .category-filter-panel label {{
            font-weight: 600;
            color: #495057;
            margin: 0;
            white-space: nowrap;
        }}
        .category-filter-panel select {{
            padding: 6px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: #fff;
            font-size: 14px;
            min-width: 150px;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        .category-filter-panel select:focus {{
            outline: none;
            border-color: #80bdff;
            box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
        }}
        .category-filter-panel button {{
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: opacity 0.15s ease-in-out;
        }}
        .category-filter-panel button:hover {{
            opacity: 0.8;
        }}
        #apply_category_filter {{
            background: #007bff;
            color: white;
        }}
        #clear_category_filter {{
            background: #6c757d;
            color: white;
        }}
        .filtered.loading {{
            opacity: 0.6;
            pointer-events: none;
            position: relative;
        }}
        .filtered.loading::after {{
            content: "Завантаження...";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 12px 20px;
            border: 1px solid #ccc;
            border-radius: 6px;
            z-index: 1000;
            font-weight: 600;
            color: #495057;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        </style>
        <div class="category-filter-panel">
            <div>
                <label>Фільтрація категорій:</label>
                <select id="category_country_filter">
                    {country_options}
                </select>
                <select id="category_continent_filter">
                    {continent_options}
                </select>
                <button type="button" id="apply_category_filter">Застосувати фільтр</button>
                <button type="button" id="clear_category_filter">Очистити</button>
            </div>
        </div>
        '''
    
    class Media:
        js = ('coins/js/category_filter_widget.js',)
        css = {
            'all': ('coins/css/category_filter_widget.css',)
        }
    
    def _media(self):
        """Додаємо JavaScript безпосередньо в HTML"""
        return forms.Media(
            js=('coins/js/category_filter_widget.js',),
            css={'all': ('coins/css/category_filter_widget.css',)}
        ) 