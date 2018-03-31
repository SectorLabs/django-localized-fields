(function($) {
    var syncTabs = function(lang) {
        $('.localized-fields-widget.tab label:contains("'+lang+'")').each(function(){
            $(this).parents('.localized-fields-widget[role="tabs"]').find('.localized-fields-widget.tab').removeClass('active');
            $(this).parents('.localized-fields-widget.tab').addClass('active');
            $(this).parents('.localized-fields-widget[role="tabs"]').children('.localized-fields-widget [role="tabpanel"]').hide();
            $('#'+$(this).attr('for')).show();
        });
    }

    $(function (){
        $('.localized-fields-widget [role="tabpanel"]').hide();
        // set first tab as active
        $('.localized-fields-widget[role="tabs"]').each(function () {
            $(this).find('.localized-fields-widget.tab:first').addClass('active');
            $('#'+$(this).find('.localized-fields-widget.tab:first label').attr('for')).show();
        });
        // try set active last selected tab
        if (window.sessionStorage) {
            var lang = window.sessionStorage.getItem('localized-field-lang');
            if (lang) {
                syncTabs(lang);
            }
        }

        $('.localized-fields-widget.tab label').click(function(event) {
            event.preventDefault();
            syncTabs(this.innerText);
            if (window.sessionStorage) {
                window.sessionStorage.setItem('localized-field-lang', this.innerText);
            }
            return false;
        });
    });
})(django.jQuery)
