// Encoding: UTF-8
// Инициализация виджета CodeMirror для редактирования Text
$(document).ready(function () {
  $('.code_editor_text').each(function (idx, el) {
    var editor = CodeMirror.fromTextArea(el, {
      lineNumbers: true,
      lineSeparator: '\n',
      indentUnit: 2, // отступ (что бы это ни значило)
      tabSize: 2,
      lineWrapping: true,  // длинные строки переносятся, а не прокручиваются
      mode: 'django',
      theme: theme_is,
      autocorrect: true,
      spellcheck: true,
      autoCloseTags: true,
      matchBrackets: true,
      lint: true,
    });
    editor.setSize('100%', 'auto');
    editor.addKeyMap({
      'Ctrl-S': function (cm) {
        $(el).closest('form').submit();
      },     // submit
      'Ctrl-F': 'findPersistent',       // поиск
    });
  });
  $('.code_editor_text + .CodeMirror .CodeMirror-lines').css('min-height', '16em');
});
