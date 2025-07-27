(function() {
    'use strict';
    
    // Функція для очікування завантаження jQuery
    function waitForJQuery(callback) {
        if (typeof jQuery !== 'undefined') {
            callback(jQuery);
        } else {
            setTimeout(function() {
                waitForJQuery(callback);
            }, 100);
        }
    }
    
    // Очікуємо завантаження jQuery
    waitForJQuery(function($) {
        $(document).ready(function() {
            // Перевіряємо чи ми на сторінці з категоріями
            if ($('#result_list').length && $('.field-ordering').length) {
                initDragAndDrop($);
            }
        });
    });
    
    // Альтернативний підхід без jQuery (якщо jQuery не завантажується)
    setTimeout(function() {
        if (typeof jQuery === 'undefined') {
            initDragAndDropVanilla();
        }
    }, 2000);
    
    function initDragAndDrop($) {
        var $tbody = $('#result_list tbody');
        var $rows = $tbody.find('tr');
        
        // Зберігаємо draggedElement в замиканні
        var dragState = {
            draggedElement: null
        };
        
        // Додаємо атрибути для drag and drop
        $rows.each(function() {
            var $row = $(this);
            $row.attr('draggable', 'true');
            $row.addClass('draggable-row');
            
            // Додаємо обробники подій з правильним контекстом
            $row.on('dragstart', function(e) { 
                dragState.draggedElement = this;
                $(this).addClass('dragging');
                e.originalEvent.dataTransfer.effectAllowed = 'move';
                e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
            });
            
            $row.on('dragend', function(e) { 
                $(this).removeClass('dragging');
                $('.drag-over').removeClass('drag-over');
                dragState.draggedElement = null;
            });
            
            $row.on('dragover', function(e) { 
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.originalEvent.dataTransfer.dropEffect = 'move';
                return false;
            });
            
            $row.on('dragenter', function(e) { 
                $(this).addClass('drag-over');
            });
            
            $row.on('dragleave', function(e) { 
                $(this).removeClass('drag-over');
            });
            
            $row.on('drop', function(e) { 
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                
                if (dragState.draggedElement !== this) {
                    var $draggedRow = $(dragState.draggedElement);
                    var $targetRow = $(this);
                    
                    // Переміщуємо елемент
                    if ($draggedRow.index() < $targetRow.index()) {
                        $targetRow.after($draggedRow);
                    } else {
                        $targetRow.before($draggedRow);
                    }
                    
                    // Оновлюємо порядок
                    updateOrdering($);
                }
                
                return false;
            });
        });
        
        addDragStyles($);
    }
    

    
    function addDragStyles($) {
        var styles = `
            .draggable-row {
                cursor: move;
                transition: all 0.2s ease;
            }
            
            .draggable-row:hover {
                background-color: #f8f9fa;
            }
            
            .dragging {
                opacity: 0.5;
                transform: rotate(2deg);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .drag-over {
                border-top: 2px solid #007bff;
                background-color: #e3f2fd;
            }
            
            .field-ordering {
                cursor: move !important;
                background-color: #f8f9fa !important;
                border: 1px solid #dee2e6 !important;
                padding: 4px 8px !important;
                border-radius: 4px !important;
                font-weight: bold !important;
                text-align: center !important;
                min-width: 40px !important;
                display: inline-block !important;
                transition: all 0.2s ease !important;
            }
            
            .field-ordering:hover {
                background-color: #e9ecef !important;
                border-color: #adb5bd !important;
                transform: scale(1.05);
            }
        `;
        
        $('<style>').html(styles).appendTo('head');
    }
    

    
    function updateOrdering($) {
        var $rows = $('#result_list tbody tr');
        var updates = [];
        
        $rows.each(function(index) {
            var $row = $(this);
            var categoryId = getCategoryId($row, $);
            
            if (categoryId) {
                updates.push({
                    category_id: categoryId,
                    ordering: index + 1
                });
            }
        });
        
        showMessage('Відбувається збереження порядку...', 'info', $);
        // Відправляємо оновлення на сервер
        if (updates.length > 0) {
            $.ajax({
                url: 'update_ordering/',
                method: 'POST',
                data: {
                    updates: JSON.stringify(updates)
                },
                success: function(response) {
                    if (response.success) {
                        // Оновлюємо відображені значення ordering
                        $rows.each(function(index) {
                            var $orderingCell = $(this).find('.field-ordering');
                            if ($orderingCell.length) {
                                $orderingCell.text(index + 1);
                            }
                        });
                        
                        // Показуємо повідомлення про успіх
                        showMessage('Порядок категорій успішно оновлено!', 'success', $);
                    } else {
                        showMessage('Помилка при оновленні порядку: ' + (response.error || 'Невідома помилка'), 'error', $);
                    }
                },
                error: function() {
                    showMessage('Помилка при з\'єднанні з сервером', 'error', $);
                }
            });
        }
    }
    
    function getCategoryId($row, $) {
        // Спробуємо різні способи отримання ID категорії
        var categoryId = $row.find('input[name="form-0-id"]').val() || 
                       $row.attr('data-id') || 
                       $row.find('td:first').text().trim();
        
        // Якщо не можемо знайти ID, спробуємо отримати з URL
        if (!categoryId || categoryId === '') {
            var $link = $row.find('a[href*="/change/"]');
            if ($link.length) {
                var href = $link.attr('href');
                var match = href.match(/\/(\d+)\/change\//);
                if (match) {
                    categoryId = match[1];
                }
            }
        }
        
        return categoryId;
    }
    
    function initDragAndDropVanilla() {
        var tbody = document.querySelector('#result_list tbody');
        if (!tbody) {
            return;
        }
        
        var rows = tbody.querySelectorAll('tr');
        var dragState = {
            draggedElement: null
        };
        
        rows.forEach(function(row) {
            row.setAttribute('draggable', 'true');
            row.classList.add('draggable-row');
            
            row.addEventListener('dragstart', function(e) {
                dragState.draggedElement = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.outerHTML);
            });
            
            row.addEventListener('dragend', function(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('.drag-over').forEach(function(el) {
                    el.classList.remove('drag-over');
                });
                dragState.draggedElement = null;
            });
            
            row.addEventListener('dragover', function(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                return false;
            });
            
            row.addEventListener('dragenter', function(e) {
                this.classList.add('drag-over');
            });
            
            row.addEventListener('dragleave', function(e) {
                this.classList.remove('drag-over');
            });
            
            row.addEventListener('drop', function(e) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                
                if (dragState.draggedElement !== this) {
                    if (dragState.draggedElement.index < this.index) {
                        this.parentNode.insertBefore(dragState.draggedElement, this.nextSibling);
                    } else {
                        this.parentNode.insertBefore(dragState.draggedElement, this);
                    }
                    updateOrderingVanilla();
                }
                
                return false;
            });
        });
        
        addDragStylesVanilla();
    }
    
    function updateOrderingVanilla() {
        var rows = document.querySelectorAll('#result_list tbody tr');
        var updates = [];
        
        rows.forEach(function(row, index) {
            var categoryId = getCategoryIdVanilla(row);
            if (categoryId) {
                updates.push({
                    category_id: categoryId,
                    ordering: index + 1
                });
            }
        });
        
        if (updates.length > 0) {
            // Отримуємо CSRF токен
            var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            var csrfValue = csrfToken ? csrfToken.value : '';
            
            showMessageVanilla('Відбувається збереження порядку...', 'info');
            fetch('update_ordering/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfValue
                },
                body: 'updates=' + encodeURIComponent(JSON.stringify(updates)) + '&csrfmiddlewaretoken=' + csrfValue
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    showMessageVanilla('Порядок категорій успішно оновлено!', 'success');
                } else {
                    showMessageVanilla('Помилка при оновленні порядку: ' + data.error, 'error');
                }
            })
            .catch(function(error) {
                showMessageVanilla('Помилка при з\'єднанні з сервером', 'error');
            });
        }
    }
    
    function getCategoryIdVanilla(row) {
        var link = row.querySelector('a[href*="/change/"]');
        if (link) {
            var href = link.getAttribute('href');
            var match = href.match(/\/(\d+)\/change\//);
            if (match) {
                return match[1];
            }
        }
        return null;
    }
    
    function showMessageVanilla(message, type) {
        var existingMessage = document.querySelector('.ordering-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        var messageDiv = document.createElement('div');
        messageDiv.className = 'ordering-message ' + (type === 'success' ? 'messagelist' : type === 'info' ? 'info' : 'errornote');
        messageDiv.textContent = message;
        
        var h1 = document.querySelector('.content h1');
        if (h1) {
            h1.parentNode.insertBefore(messageDiv, h1.nextSibling);
        }
        
        setTimeout(function() {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 3000);
    }
    
    function addDragStylesVanilla() {
        var style = document.createElement('style');
        style.textContent = `
            .draggable-row {
                cursor: move;
                transition: all 0.2s ease;
            }
            .draggable-row:hover {
                background-color: #f8f9fa;
            }
            .dragging {
                opacity: 0.5;
                transform: rotate(2deg);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .drag-over {
                border-top: 2px solid #007bff;
                background-color: #e3f2fd;
            }
            .field-ordering {
                cursor: move !important;
                background-color: #f8f9fa !important;
                border: 1px solid #dee2e6 !important;
                padding: 4px 8px !important;
                border-radius: 4px !important;
                font-weight: bold !important;
                text-align: center !important;
                min-width: 40px !important;
                display: inline-block !important;
                transition: all 0.2s ease !important;
            }
            .field-ordering:hover {
                background-color: #e9ecef !important;
                border-color: #adb5bd !important;
                transform: scale(1.05);
            }
        `;
        document.head.appendChild(style);
    }
    
    function showMessage(message, type, $) {
        // Видаляємо попередні повідомлення
        $('.ordering-message').remove();
        
        var cssClass = type === 'success' ? 'messagelist' : type === 'info' ? 'info' : 'errornote';
        var $message = $('<div class="ordering-message ' + cssClass + '">' + message + '</div>');
        
        // Додаємо повідомлення після заголовка
        $('.content h1').after($message);
        
        // Автоматично видаляємо повідомлення через 3 секунди
        setTimeout(function() {
            $message.fadeOut(function() {
                $(this).remove();
            });
        }, 3000);
    }
    
})(django.jQuery); 