jQuery(document).ready(function ($) {
    // Функція для отримання поточних URL параметрів
    function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params.entries()) {
            if (result[key]) {
                // Якщо ключ вже існує, робимо масив
                if (Array.isArray(result[key])) {
                    result[key].push(value);
                } else {
                    result[key] = [result[key], value];
                }
            } else {
                result[key] = value;
            }
        }
        return result;
    }

    // Функція для оновлення URL з новими параметрами
    function updateUrl(params, resetPage = true) {
        const urlParams = new URLSearchParams();
        
        // Додаємо всі параметри
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined && params[key] !== '' && params[key] !== 'undefined') {
                if (Array.isArray(params[key])) {
                    params[key].forEach(val => {
                        if (val) urlParams.append(key, val);
                    });
                } else {
                    urlParams.set(key, params[key]);
                }
            }
        });
        
        // Скидаємо page при зміні фільтрів
        if (resetPage) {
            urlParams.delete('page');
        }
        
        // Оновлюємо URL без перезавантаження сторінки
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.pushState({}, '', newUrl);
        
        // Перезавантажуємо сторінку для оновлення результатів
        window.location.href = newUrl;
    }

    // Обробка кліку на фільтри (continent, country, type, category, sort)
    $('.filter-link').on('click', function(e) {
        e.preventDefault();
        const filterType = $(this).data('filter-type');
        const filterValue = $(this).data('filter-value');
        const currentParams = getUrlParams();
        
        // Оновлюємо параметр
        if (filterValue === '' || filterValue === null) {
            delete currentParams[filterType];
        } else {
            currentParams[filterType] = filterValue;
        }
        
        // Логіка залежностей
        if (filterType === 'continent') {
            // При зміні континенту скидаємо країну (перевірка на сервері)
            if (filterValue) {
                delete currentParams.country;
            }
        }
        if (filterType === 'type') {
            // При зміні типу скидаємо категорію (перевірка на сервері)
            if (filterValue) {
                delete currentParams.category;
            }
        }
        
        updateUrl(currentParams, true);
    });

    // Обробка checkbox для denomination
    $('.filter-checkbox[name="denomination"]').on('change', function() {
        const currentParams = getUrlParams();
        const checkedDenominations = [];
        
        $('.filter-checkbox[name="denomination"]:checked').each(function() {
            checkedDenominations.push($(this).val());
        });
        
        if (checkedDenominations.length > 0) {
            currentParams.denomination = checkedDenominations;
        } else {
            delete currentParams.denomination;
        }
        
        updateUrl(currentParams, true);
    });

    // Обробка material через filter-link (тепер це dropdown, а не select)
    // Логіка вже обробляється через загальний обробник .filter-link

    // Обробка select для sort
    $('.filter-select[name="sort"]').on('change', function() {
        const currentParams = getUrlParams();
        const value = $(this).val();
        
        if (value && value !== '--' && value !== '') {
            currentParams.sort = value;
        } else {
            delete currentParams.sort;
        }
        
        updateUrl(currentParams, true);
    });

    // Обробка input для years з debounce
    let yearTimeout;
    $('.filter-input[name="min_year"], .filter-input[name="max_year"]').on('input', function() {
        clearTimeout(yearTimeout);
        yearTimeout = setTimeout(function() {
            const currentParams = getUrlParams();
            const minYear = $('input[name="min_year"]').val();
            const maxYear = $('input[name="max_year"]').val();
            
            if (minYear) {
                currentParams.min_year = minYear;
            } else {
                delete currentParams.min_year;
            }
            
            if (maxYear) {
                currentParams.max_year = maxYear;
            } else {
                delete currentParams.max_year;
            }
            
            updateUrl(currentParams, true);
        }, 500); // Затримка 500мс після останнього введення
    });

    // Обробка кнопки Reset
    $('#resetFilters').on('click', function(e) {
        e.preventDefault();
        // Перенаправляємо на сторінку без параметрів
        window.location.href = window.location.pathname;
    });

    // Обробка видалення фільтрів через chips
    $('[data-remove-filter]').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const filterType = $(this).data('remove-filter');
        const filterValue = $(this).data('filter-value');
        const currentParams = getUrlParams();
        
        if (filterType === 'years') {
            delete currentParams.min_year;
            delete currentParams.max_year;
        } else if (filterType === 'denomination' && filterValue) {
            // Видаляємо конкретний denomination з масиву
            if (Array.isArray(currentParams.denomination)) {
                currentParams.denomination = currentParams.denomination.filter(v => v !== filterValue);
                if (currentParams.denomination.length === 0) {
                    delete currentParams.denomination;
                }
            } else {
                delete currentParams.denomination;
            }
        } else {
            delete currentParams[filterType];
        }
        
        updateUrl(currentParams, true);
    });

    // Оновлення вигляду dropdown для sort
    $('#sortByList li.filter-link').on('click', function(e) {
        e.preventDefault();
        $('#sortByList li').removeClass('active');
        $(this).addClass('active');
        
        const sortValue = $(this).data('filter-value');
        $('#sortSelect').val(sortValue);
        
        const currentParams = getUrlParams();
        if (sortValue && sortValue !== '--') {
            currentParams.sort = sortValue;
        } else {
            delete currentParams.sort;
        }
        
        updateUrl(currentParams, true);
    });

    // Пошук в категоріях
    $('#categorySearch').on('input', function() {
        const searchText = $(this).val().toLowerCase().trim();
        const categoryItems = $('.category-item');
        
        if (searchText === '') {
            // Показуємо всі категорії
            categoryItems.show();
        } else {
            // Фільтруємо категорії
            categoryItems.each(function() {
                const categoryName = $(this).data('category-name');
                if (categoryName && categoryName.includes(searchText)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }
    });

    // Універсальна функція для пошуку в dropdown
    function setupDropdownSearch(searchInputId, itemClass) {
        $(searchInputId).on('input', function() {
            const searchText = $(this).val().toLowerCase().trim();
            const items = $(itemClass);
            
            if (searchText === '') {
                items.show();
            } else {
                items.each(function() {
                    const itemName = $(this).data('item-name');
                    if (itemName && itemName.includes(searchText)) {
                        $(this).show();
                    } else {
                        $(this).hide();
                    }
                });
            }
        });

        // Запобігаємо закриттю dropdown при кліку на поле пошуку
        $(searchInputId).on('click', function(e) {
            e.stopPropagation();
        });
    }

    // Налаштування пошуку для всіх dropdown
    setupDropdownSearch('#typeSearch', '.type-item');
    setupDropdownSearch('#continentSearch', '.continent-item');
    setupDropdownSearch('#countrySearch', '.country-item');
    setupDropdownSearch('#denominationSearch', '.denomination-item');
    setupDropdownSearch('#materialSearch', '.material-item');

    // Оновлення тексту кнопки material при виборі
    $('.filter-link[data-filter-type="material"]').on('click', function() {
        const materialValue = $(this).data('filter-value');
        const materialText = materialValue ? $(this).text().trim() : 'Material';
        $('#btnGroupDropMaterial').html(materialText);
    });
});

