from telebot import types

functionalKeyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
butFunc1 = types.KeyboardButton('Сделать анализ по общим пользователям')
butFunc2 = types.KeyboardButton('Найти вектор комментариев')
functionalKeyboard.add(butFunc1, butFunc2)

cycleKeyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
btnCycle1 = types.KeyboardButton('Остановить')
btnCycle2 = types.KeyboardButton('Показать результат')
cycleKeyboard.add(btnCycle1, btnCycle2)

cycle2Keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
btn2Cycle1 = types.KeyboardButton('Остановить')
cycle2Keyboard.add(btn2Cycle1)

adminPanel = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
adBut1 = types.KeyboardButton('Добавить админа')
adBut2 = types.KeyboardButton('Посмотреть уникальных пользователей')
adBut3 = types.KeyboardButton('Посмотреть историю обращений')
adBut4 = types.KeyboardButton('Вернуться')
adminPanel.add(adBut1, adBut2, adBut3, adBut4)
