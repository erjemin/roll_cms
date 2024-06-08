// Включаем "темную" или "светлую" тему в зависимости от настроек браузера пользователя
var theme_is = 'solarized'; // светлая тема
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) theme_is = 'rubyblue';  // тёмная тема
