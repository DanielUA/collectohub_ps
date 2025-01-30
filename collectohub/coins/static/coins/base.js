jQuery("document").ready(function ($) {
    $('.select-all').on('change', function(){
        if ($(this).prop("checked")){
            $('[name="coins"]').prop('checked', 'checked')
        } else {
            $('[name="coins"]').prop('checked', false)
        }
    })
});