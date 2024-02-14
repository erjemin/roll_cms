// Этот файл нужен для инициализации jinja-редактора шаблонов codemirror в админке
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        var theme_is = 'rubyblue';
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            theme_is = 'ides';  // dark mode
        }
        $('.code_editor').each(function(idx, el){
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                tabSize: 2,
                mode: 'text/html',
                // mode: 'htmlmixed',
                // mode: 'xml',
                // mode: 'jinja2',
                gutters: ['CodeMirror-lint-markers'],
                theme: theme_is,
                lint: true,
                autoCloseTags: true,
                matchBrackets: true,
            });
        });
        $('.code_editor').each(function(idx, el){
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                tabSize: 2,
                // mode: 'text/html',
                // mode: 'htmlmixed',
                // mode: 'xml',
                mode: 'jinja2',
                gutters: ['CodeMirror-lint-markers'],
                theme: theme_is,
                lint: true,
                autoCloseTags: true,
                matchBrackets: true,

            });
        });
    });
})();