// Этот файл нужен для инициализации jinja-редактора шаблонов codemirror в админке
(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        $('.html-editor').each(function(idx, el){
            function getSelectedRange() {
                return { from: editor.getCursor(true), to: editor.getCursor(false) };
            }
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                tabSize: 2,
                mode: 'text/html',
                gutters: ['CodeMirror-lint-markers'],
                theme: 'rubyblue',
                lint: true,
                // json: true,
            });
            CodeMirror.commands["selectAll"](editor);
            var range = getSelectedRange();
            editor.autoFormatRange(range.from, range.to);

            range = getSelectedRange();
            editor.commentRange(false, range.from, range.to);
        });
    });
})();