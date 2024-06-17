// Encoding: UTF-8
// Инициализация виджета CodeMirror для редактирования Title (заголовков)
$(document).ready(function () {
  function no_num() {
    return function (line) {
      return '>>';
    };
  }

  $('.url_str').each(function (idx, el){
    var editor = CodeMirror.fromTextArea(el, {
      lineNumbers: true,
      lineNumberFormatter: no_num(),
      // lineSeparator: '',
      fixedGutter: true,
      indentUnit: 0, // отступ (что бы это ни значило)
      tabSize: 0,
      lineWrapping: true,  // длинные строки переносятся, а не прокручиваются
      mode: 'text/html',
      // gutters: ['CodeMirror-lint-markers'],
      theme: theme_is,
      autocorrect: true,
      lint: true,
    });
    editor.setSize('100%', 'auto');
  });
});