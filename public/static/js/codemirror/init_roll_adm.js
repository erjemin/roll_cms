// Этот файл нужен для инициализации json-редактора codemirror в админке

// инициализация codemirror
// рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
(function () {
  var $ = django.jQuery;
  $(document).ready(function () {
    // Включаем "темную" или "светлую" тему в зависимости от настроек браузера пользователя
    var theme_is = 'idea'; // светлая тема
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) theme_is = 'rubyblue';  // тёмная тема
    // инициализация codemirror для json
    // $('#id_szRollOldSlugs').each(function (idx, el) {
    //   var editor = CodeMirror.fromTextArea(el, {
    //     lineNumbers: true,
    //     mode: 'html',
    //     gutters: ['CodeMirror-lint-markers'],
    //     theme: theme_is,
    //     lint: true
    //   });
    //   CodeMirror.commands["selectAll"](editor);
    //   var range = getSelectedRange();
    //   editor.autoFormatRange(range.from, range.to);
    //
    //   range = getSelectedRange();
    //   editor.commentRange(false, range.from, range.to);
    // });

    $('.json_editor').each(function (idx, el) {
      var editor = CodeMirror.fromTextArea(el, {
        lineNumbers: true,
        tabSize: 2,
        mode: 'application/json',   // application/lg+json
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
        },     // submit
        'Ctrl-F': 'findPersistent',       // поиск
      });
    });
  });
})();