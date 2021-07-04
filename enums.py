from enum import Enum


class ButtonsType(Enum):
    AdminPanel = 'admin'
    FunctionalPanel = 'select_func'
    SelectFirstFunction = 'first_func'
    SelectSecondFunction = 'second_func'
    RemoveButtons = 'remove'
    Stop = 'Остановить'
    ShowResult = 'Показать результат'
    FirstFunction = 'Сделать анализ по общим пользователям'
    SecondFunction = 'Найти вектор комментариев'
    AddAdmin = 'Добавить админа'
    ShowUniqueUsers = 'Посмотреть уникальных пользователей'
    ShowHistory = 'Посмотреть историю обращений'
    Back = 'Вернуться'


class ErrorsType(Enum):
    Welcome = open('helpingFiles/Welcome.txt').read()
    EndingFirstFunc = open('helpingFiles/EndFirstFunc.txt').read()
    ErrorInputGroup = open('helpingFiles/ErrorFoundGroup.txt').read()
    ErrorFoundComments = open('helpingFiles/ErrorFoundComments.txt').read()
    ErrorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt').read()
