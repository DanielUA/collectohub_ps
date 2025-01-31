jQuery("document").ready(function ($) {
    $('.select-all').on('change', function(){
        if ($(this).prop("checked")){
            $('[name="coins"]').prop('checked', 'checked')
        } else {
            $('[name="coins"]').prop('checked', false)
        }
    })

    // Функція для збереження фільтрів у кукі
    function saveFiltersToCookies() {
        const startYear = $('input[name="min_year"]').val();
        const endYear = $('input[name="max_year"]').val();
        const denomination = [];
        $('input[name="denomination"]:checked').each(function() {
            denomination.push($(this).val());
        });

        // Зберігаємо значення у кукі
        document.cookie = `min_year=${startYear}; path=/`;
        document.cookie = `max_year=${endYear}; path=/`;
        document.cookie = `denomination=${denomination.join(',')}; path=/`;
    }

    // Функція для завантаження фільтрів з кукі
    function loadFiltersFromCookies() {
        const cookies = document.cookie.split(';').reduce((acc, cookie) => {
            const [key, value] = cookie.trim().split('=');
            acc[key] = value;
            return acc;
        }, {});

        // Заповнюємо поля фільтрів
        if (cookies.min_year) {
            $('input[name="min_year"]').val(cookies.min_year);
        }
        if (cookies.max_year) {
            $('input[name="max_year"]').val(cookies.max_year);
        }
        if (cookies.denomination) {
            const denomination = cookies.denomination.split(',');
            $('input[name="denomination"]').each(function() {
                if (denomination.includes($(this).val())) {
                    $(this).prop('checked', true);
                }
            });
        }
    }

    // Подія для кнопки "Confirm filters"
    $('.confirm_filters').on('click', function(e) {
        console.log('filt')
        e.preventDefault(); // Забороняємо стандартну поведінку форми
        saveFiltersToCookies(); // Зберігаємо фільтри у кукі
        window.location.reload(); // Перезавантажуємо сторінку
    });

    // Завантажуємо фільтри з кукі при завантаженні сторінки
    loadFiltersFromCookies();

    // Функція для перевірки наявності кукі
    function checkCookies() {
        const cookies = document.cookie.split(';').reduce((acc, cookie) => {
            const [key, value] = cookie.trim().split('=');
            acc[key] = value;
            return acc;
        }, {});

        // Якщо є кукі, показуємо кнопку "Видалити фільтри"
        if (cookies.min_year || cookies.max_year || cookies.denomination) {
            $('#resetFilters').show();
        }
    }

    // Функція для видалення кукі
    function deleteCookies() {
        document.cookie = 'min_year=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        document.cookie = 'max_year=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        document.cookie = 'denomination=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        window.location.reload(); // Перезавантажуємо сторінку
    }

    // Перевіряємо наявність кукі при завантаженні сторінки
    checkCookies();

    // Подія для кнопки "Видалити фільтри"
    $('#resetFilters').on('click', function() {
        deleteCookies();
    });
});