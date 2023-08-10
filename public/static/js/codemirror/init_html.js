// Этот файл нужен для инициализации jinja-редактора шаблонов codemirror в админке
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        $('.code_editor').each(function(idx, el){
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                tabSize: 2,
                // mode: 'text/html',
                // mode: 'xml',
                mode: 'htmlmixed',
                gutters: ['CodeMirror-lint-markers'],
                theme: 'rubyblue',
                json: true,
                lint: true,
                autoCloseTags: true,
                matchBrackets: true,
            });
            editor.setSize('170ex', 'auto');  // Ширина 120 знаков... высота авто (вертикальная прокрутка не появляется)
        });
    });
})();