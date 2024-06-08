// Encoding: UTF-8
// Инициализация виджета CodeMirror для редактирования JSON (однострочный)
$(document).ready(function () {
  // инициализация codemirror для json
  $('.json_editor1').each(function (idx, el) {
    var editor = CodeMirror.fromTextArea(el, {
      lineNumbers: true,
      tabSize: 2,
      mode: 'application/json',
      lineWrapping: true,  // длинные строки переносятся, а не прокручиваются
      // readOnly: 'nocursor',
      undoDepth: 20,
      // gutters: ['CodeMirror-lint-markers'],
      theme: theme_is,
      lint: true,
      autoCloseTags: true,
      matchBrackets: true,
    });
    editor.setSize('100%', 'auto');
  });
});