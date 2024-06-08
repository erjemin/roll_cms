// Encoding: UTF-8
// Инициализация виджета CodeMirror для редактирования Title (заголовков)
$(document).ready(function () {
  $('.code_editor_title').each(function (idx, el){
    var editor = CodeMirror.fromTextArea(el, {
      lineNumbers: true,
      lineSeparator: '\n',
      indentUnit: 2, // отступ (что бы это ни значило)
      tabSize: 2,
      lineWrapping: true,  // длинные строки переносятся, а не прокручиваются
      mode: 'text/html',
      // gutters: ['CodeMirror-lint-markers'],
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
});