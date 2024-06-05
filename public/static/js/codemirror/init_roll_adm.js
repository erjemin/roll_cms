// Этот файл нужен для инициализации json-редактора codemirror в админке

// инициализация codemirror
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function () {
  var $ = django.jQuery;
  $(document).ready(function () {
    // Включаем "темную" или "светлую" тему в зависимости от настроек браузера пользователя
    var theme_is = 'solarized'; // светлая тема
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) theme_is = 'rubyblue';  // тёмная тема

    // инициализация codemirror для Заголовка (title) в формате html-кода
    $('.code_editor_title').each(function (idx, el) {
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


    // инициализация codemirror для Заголовка (title) в формате html-кода
    $('.code_editor_text').each(function (idx, el) {
      var editor = CodeMirror.fromTextArea(el, {
        lineNumbers: true,
        lineSeparator: '\n',
        indentUnit: 2, // отступ (что бы это ни значило)
        tabSize: 2,
        lineWrapping: true,  // длинные строки переносятся, а не прокручиваются
        mode: 'django',
        // gutters: ['CodeMirror-lint-markers'],
        theme: theme_is,
        autocorrect: true,
        spellcheck: true,
        autoCloseTags: true,
        matchBrackets: true,
        lint: true,
      });
      editor.setSize('100%');
      editor.addKeyMap({
        'Ctrl-S': function (cm) {
          $(el).closest('form').submit();
        },     // submit
        'Ctrl-F': 'findPersistent',       // поиск
      });
    });

    // инициализация codemirror для json
    $('.json_editor').each(function (idx, el) {
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
})();