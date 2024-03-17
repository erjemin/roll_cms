// Этот файл нужен для инициализации jinja-редактора шаблонов codemirror в админке
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function () {
  var $ = django.jQuery;
  $(document).ready(function () {
    var theme_is = 'idea';
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) theme_is = 'rubyblue';  // dark mode

    CodeMirror.defineMode("html+jinja2{}", function (config) {
      return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "text/html"), {
          open: "{{", close: "}}",
          mode: CodeMirror.getMode(config, "jinja2"),
          parseDelimiters: true,
        }
        );
    });

    CodeMirror.defineMode("html+jinja2##", function (config) {
      return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "html+jinja2{}"), {
          open: "{#", close: "#}",
          mode: CodeMirror.getMode(config, "jinja2"),
          parseDelimiters: true,
        }
        );
    });
        CodeMirror.defineMode("html+jinja2", function (config) {
      return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "html+jinja2##"), {
          open: "{%", close: "%}",
          mode: CodeMirror.getMode(config, "jinja2"),
          parseDelimiters: true,
        }
        );
    });



    $('#code_editor').each(function (idx, el) {
      var editor = CodeMirror.fromTextArea(el, {
        lineNumbers: true,
        tabSize: 2,
        mode: 'html+jinja2',
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
        'Ctrl-S': function (cm) {
          $(el).closest('form').submit();
        }, // submit form
        'Ctrl-F': 'findPersistent', // search
      });
      // editor.setOption('mode', 'jinja2');
      // editor.save();
    });

  });
})();