// Этот файл нужен для инициализации html+jinja-редактора шаблонов codemirror в админке Django
// рецепт написал сам: https://qna.habr.com/q/1284408
$(document).ready(function () {
  // Включаем подсветку jinja-тегов {{...}} внутри html
  CodeMirror.defineMode("html+jinja2{}", function (config) {
    return CodeMirror.multiplexingMode(
      CodeMirror.getMode(config, "django"), {  // text/html
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

  // инициализация codemirror для Jinja+Htm;
  $('.code_editor').each(function (idx, el) {
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
  $('.code_editor + .CodeMirror .CodeMirror-lines').css('min-height', '18em');
});