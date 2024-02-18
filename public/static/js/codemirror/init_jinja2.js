// Этот файл нужен для инициализации jinja-редактора шаблонов codemirror в админке
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function(){
    // проверим темная или светлая тема у пользователя
    var theme = 'idea';
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
        theme = 'rubyblue';
    var $ = django.jQuery;
    $(document).ready(function(){
        $('.code_editor').each(function(idx, el){
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                tabSize: 2,
                // mode: 'text/html',
                // mode: 'htmlmixed',
                // mode: 'xml',
                mode: 'text/jinja2',
                gutters: ['CodeMirror-lint-markers'],
                theme: theme,
                lint: true,
                autoCloseTags: true,
                matchBrackets: true,
            });

            // CodeMirror.commands["selectAll"](editor); // выделить все
            editor = CodeMirror.fromTextArea(el, {
                mode: 'text/html',
                theme: theme,
            });
            editor.setSize('170ex', 'auto');  // Ширина 120 знаков... высота авто (вертикальная прокрутка не появляется)
            // var range = getSelectedRange();
            // editor.autoFormatRange(range.from, range.to);
            // range = getSelectedRange();
            // editor.commentRange(false, range.from, range.to);
        });
    });
})();