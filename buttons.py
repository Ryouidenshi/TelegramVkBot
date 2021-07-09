from telebot import types

import enums


class Buttons:
    @staticmethod
    def createButton(name):
        if name == enums.ButtonsType.FunctionalPanel:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Сделать анализ по общим пользователям')
            buttonSecond = types.KeyboardButton('Найти вектор комментариев')
            buttonThird = types.KeyboardButton('Избранные группы ⭐')
            keyboard.add(buttonFirst, buttonThird, buttonSecond)
            return keyboard
        elif name == enums.ButtonsType.AdminPanel:
            keyboard = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Добавить модератора')
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
        elif name == enums.ButtonsType.ModeratorPanel:
            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Посмотреть уникальных пользователей')
            buttonSecond = types.KeyboardButton('Посмотреть историю обращений')
            buttonThird = types.KeyboardButton('Вернуться')
            keyboard.add(buttonFirst, buttonSecond, buttonThird)
            return keyboard
        elif name == enums.ButtonsType.YesOrNo:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            buttonFirst = types.KeyboardButton('Да ✅')
            buttonSecond = types.KeyboardButton('Нет ❌')
            keyboard.add(buttonFirst, buttonSecond)
            return keyboard
        elif name == enums.ButtonsType.ActualButtons:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            buttonFirst = types.KeyboardButton(enums.ButtonsType.GetActual.value)
            buttonSecond = types.KeyboardButton(enums.ButtonsType.UseExists.value)
            keyboard.add(buttonFirst, buttonSecond)
            return keyboard
        elif name == enums.ButtonsType.Stop:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button = types.KeyboardButton(enums.ButtonsType.Stop.value)
            keyboard.add(button)
            return keyboard
