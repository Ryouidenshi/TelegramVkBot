from telebot import types

functionalKeyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
butFunc1 = types.KeyboardButton('Сделать анализ по общим пользователям')
butFunc2 = types.KeyboardButton('Найти вектор комментариев')
functionalKeyboard .add(butFunc1, butFunc2)


cycleKeyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
btnCycle1 = types.KeyboardButton('Остановить')
btnCycle2 = types.KeyboardButton('Показать результат')
cycleKeyboard.add(btnCycle1, btnCycle2)

