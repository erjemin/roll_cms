// Encoding: UTF-8
// Инициализация виджета CodeMirror для редактирования JSON (трех строчный)
$(document).ready(function () {
  // инициализация codemirror для json
  $('.json_editor2').each(function (idx, el) {
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
  // Зададим min-height для блока редактора (элемент .CodeMirror-lines вложенный в .CodeMirror и следующий за .json_editor2)
  $('.json_editor2 + .CodeMirror .CodeMirror-lines').css('min-height', '6em');
});