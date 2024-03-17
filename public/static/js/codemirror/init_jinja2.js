// Этот файл нужен для инициализации html+jinja-редактора шаблонов codemirror в админке Django
// рецепт написал сам: https://qna.habr.com/q/1284408
(function () {
  var $ = django.jQuery;
  $(document).ready(function () {
    // Включаем "темную" или "светлую" тему в зависимости от настроек браузера пользователя
    var theme_is = 'idea';
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) theme_is = 'rubyblue';  // dark mode

    // Включаем подсветку jinja-тегов {{...}} внутри html
    CodeMirror.defineMode("html+jinja2{}", function (config) {
      return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "text/html"), {
          open: "{{", close: "}}",
          mode: CodeMirror.getMode(config, "jinja2"),
          parseDelimiters: true,
        }
        );
    });

    // Включаем подсветку jinja2-тегов {%...%}
    CodeMirror.defineMode("html+jinja2%%", function (config) {
      return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "html+jinja2{}"), {
          open: "{%", close: "%}",
          mode: CodeMirror.getMode(config, "jinja2"),
          parseDelimiters: true,
        }
        );
    });

    // Включаем подсветку jinja2-комментариев {#...#}
    CodeMirror.defineMode("html+jinja2", function (config) {
      return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "html+jinja2%%"), {
          open: "{#", close: "#}",
          mode: CodeMirror.getMode(config, "jinja2"),
          parseDelimiters: true,
        }
        );
    });

    // инициализация codemirror
    $('#code_editor').each(function (idx, el) {
      var editor = CodeMirror.fromTextArea(el, {
        lineNumbers: true,
        tabSize: 2,
        mode: 'html+jinja2',
        gutters: ['CodeMirror-lint-markers'],
        theme: theme_is,
        lint: true,
        autoCloseTags: true,
        matchBrackets: true,
      });
      editor.setSize('120em', 'auto');
      editor.addKeyMap({
        'Ctrl-S': function (cm) {$(el).closest('form').submit(); },     // submit
        'Ctrl-F': 'findPersistent',       // поиск
      });
    });
  });
})();