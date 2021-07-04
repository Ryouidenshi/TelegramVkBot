from telebot import types

import enums

class Buttons:

    def __init__(self, type_buttons):
        self.type_buttons = type_buttons

    def createButton(self, name):
        if self.type_buttons == 'unusual':
            return
        if name == enums.ButtonsType.FunctionalPanel:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Сделать анализ по общим пользователям')
            buttonSecond = types.KeyboardButton('Найти вектор комментариев')
            keyboard.add(buttonFirst, buttonSecond)
            return keyboard
        elif name == enums.ButtonsType.AdminPanel:
            keyboard = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Добавить админа')
            buttonSecond = types.KeyboardButton('Посмотреть уникальных пользователей')
            buttonThird = types.KeyboardButton('Посмотреть историю обращений')
            buttonFourth = types.KeyboardButton('Вернуться')
            keyboard.add(buttonFirst, buttonSecond, buttonThird, buttonFourth)
            return keyboard
        elif name == enums.ButtonsType.SelectFirstFunction:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Остановить')
            buttonSecond = types.KeyboardButton('Показать результат')
            keyboard.add(buttonFirst, buttonSecond)
            return keyboard
        elif name == enums.ButtonsType.SelectSecondFunction:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Остановить')
            keyboard.add(buttonFirst)
            return keyboard
        elif name == enums.ButtonsType.RemoveButtons:
            return types.ReplyKeyboardRemove()
