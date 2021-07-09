from enum import Enum


class ButtonsType(Enum):
    AdminPanel = 'admin'
    ModeratorPanel = 'moderator'
    FunctionalPanel = 'select_func'
    SelectFirstFunction = 'first_func'
    SelectSecondFunction = 'second_func'
    RemoveButtons = 'remove'
    YesOrNo = 'yesOrNo'
    ActualButtons = 'actual'
    Stop = 'Остановить'
    ShowResult = 'Показать результат'
    FirstFunction = 'Сделать анализ по общим пользователям'
    SecondFunction = 'Найти вектор комментариев'
    AddModerator = 'Добавить модератора'
    ShowUniqueUsers = 'Посмотреть уникальных пользователей'
    ShowCountStarts = 'Посмотреть историю обращений'
    ShowHistory = 'Посмотреть историю запросов'
    Back = 'Вернуться'
    Yes = 'Да ✅'
    Favorite = 'Избранные группы ⭐'
    GetActual = 'Актуализировать 🔄'
    UseExists = 'Использовать имеющиеся 📚'


class ErrorsType(Enum):
    Welcome = open('samplesErrors/Welcome.txt').read()
    EndingFirstFunc = open('samplesErrors/EndFirstFunc.txt').read()
    ErrorInputGroup = open('samplesErrors/ErrorFoundGroup.txt').read()
    ErrorFoundComments = open('samplesErrors/ErrorFoundComments.txt').read()
    ErrorFoundGroup = open('samplesErrors/ErrorFoundGroup.txt').read()


class HistoryText(Enum):
    start = 'Запуск бота'
    history = 'Запрос истории запросов'
    admin_try = 'Попытка авторизации в административной панели'
    admin_login = 'Успешная авторизация в административной панели'
    view_unique = 'Просмотр уникальных пользователей'
    admin_history = 'Просмотр истории запросов пользователя'
    add_admin = 'Добавление администратора/модератора'
    help = 'Вызов помощи'
    favorites = 'Просмотр избранного'
    comments = 'Анализ комментариев'
    groups = 'Подсчет общих подписчиков'
