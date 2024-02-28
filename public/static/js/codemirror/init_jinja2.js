// Этот файл нужен для инициализации jinja-редактора шаблонов codemirror в админке
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        var theme_is = 'rubyblue';
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) theme_is = 'ides';  // dark mode

        CodeMirror.defineMode("htmljinja2", function(config) {
            return CodeMirror.multiplexingMode(
                CodeMirror.getMode(config, "text/html"), {
                    open: "{%", close: "%}",
                    mode: CodeMirror.getMode(config, "jinja2"),
                    delimStyle: "delimit",
                });
        });


        $('#code_editor').each(function(idx, el){
            var editor = CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                tabSize: 2,
                mode: 'htmljinja2',
                // mode: 'text/html',
                // mode: 'xml',
                // mode: 'jinja2',
                gutters: ['CodeMirror-lint-markers'],
                theme: theme_is,
                lint: true,
                autoCloseTags: true,
                matchBrackets: true,
            });
            editor.setSize('120em', 'auto');
            editor.addKeyMap({
                'Ctrl-S': function(cm) {$(el).closest('form').submit();}, // submit form
                'Ctrl-F': 'findPersistent', // search
            });
            // editor.setOption('mode', 'jinja2');
            // editor.save();
        });

    });
})();