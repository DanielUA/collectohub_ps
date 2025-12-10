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
        const sort = $('select[name="sort"]').val();
        const startYear = $('input[name="min_year"]').val();
        const endYear = $('input[name="max_year"]').val();
        const material = $('input[name="material"]:checked').val();
        const denomination = [];
        $('input[name="denomination"]:checked').each(function() {
            denomination.push($(this).val());
        });

        // Зберігаємо значення у кукі
        document.cookie = `min_year=${startYear}; path=/`;
        document.cookie = `max_year=${endYear}; path=/`;
        document.cookie = `denomination=${denomination.join(',')}; path=/`;
        document.cookie = `material=${material}; path=/`;
        document.cookie = `sort=${sort}; path=/`;
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
        if (cookies.material) {
            $('input[name="material"]').each(function() {
                if (cookies.material.includes($(this).val())) {
                    $(this).prop('checked', true);
                }
            });
        }
        if (cookies.sort) {
            $('#sortByList li[data-sort="' + cookies.sort + '"]').addClass('active');
            if (cookies.sort != '--') {
                $('#sortBy').html($('#sortByList li[data-sort="' + cookies.sort + '"]').html());
            }
            $('select[name="sort"]').val(cookies.sort);
        }
    }

    // Подія для кнопки "Confirm filters"
    $('.confirm_filters').on('click', function(e) {
        e.preventDefault(); // Забороняємо стандартну поведінку форми
        saveFiltersToCookies(); // Зберігаємо фільтри у кукі
        window.location.reload(); // Перезавантажуємо сторінку
    });
    
    $('body').on('click', '#sortByList li', function() {
        $('#sortByList li').removeClass('active');
        $(this).addClass('active');
        if ($(this).data('sort') != '--') {
            $('#sortBy').html($(this).html());
        }
        const sort = $(this).data('sort');
        $('select[name="sort"]').val(sort);
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