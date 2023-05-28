// Этот файл нужен для инициализации json-редактора codemirror в админке

// инициализация codemirror
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        $('.json-editor').each(function(idx, el){
            function getSelectedRange() {
                return { from: editor.getCursor(true), to: editor.getCursor(false) };
            }
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                mode: 'application/json',
                gutters: ['CodeMirror-lint-markers'],
                theme: 'rubyblue',
                lint: true
            });
            CodeMirror.commands["selectAll"](editor);
            var range = getSelectedRange();
            editor.autoFormatRange(range.from, range.to);

            range = getSelectedRange();
            editor.commentRange(false, range.from, range.to);
        });
    });
})();