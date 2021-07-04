from __future__ import unicode_literals
import telebot
import parserComments
from telebot import types
import buttons
import group
import graph
import vectors
import parserUsers

token = "925362923:AAFyL5YbToopgDHSI1pINKDMSdgmn4Yb6EU"

bot = telebot.TeleBot(token)

welcome = open('helpingFiles/Welcome.txt').read()

endingFirstFunc = open('helpingFiles/EndFirstFunc.txt').read()

errorInputGroup = open('helpingFiles/ErrorFoundGroup.txt').read()

errorFoundComments = open('helpingFiles/ErrorFoundComments.txt').read()

errorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt').read()

listAdmin = [402294298]

numberGroupUsers = 1

numberImageComments = 1


def write_start_message(message):
    bot.reply_to(message,
                 welcome + "\n\n"
                           "Используйте следующие команды:\n"
                           "/help - помощь\n"
                           "/startbot - запустить бота\n"
                           "/history - история запросов")


@bot.message_handler(commands=['start'])
def start_message(message: types.Message):
    global listAdmin
    bot.send_photo(message.chat.id, photo=open('data/pre.jpg', 'rb'), reply_markup=types.ReplyKeyboardRemove())
    write_start_message(message)


@bot.message_handler(commands=['history'])
def start_history(message: types.Message):
    return message
    # тут необходимо реализовать историю запросов для пользователя


@bot.message_handler(commands=['admin'])
def start_admin(message: types.Message):
    if message.from_user.id not in listAdmin:
        bot.send_message(message.chat.id, 'У вас нет прав доступа к данному разделу.',
                         reply_markup=buttons.functionalKeyboard)
        start_message(message)
    else:
        f = bot.send_message(message.chat.id, 'Авторизация прошла успешно. Выберите функцию.',
                             reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(f, select_funcAdmin)


def select_funcAdmin(message):
    if message.text == 'Добавить админа':
        idUser = bot.send_message(message.chat.id, 'Введите id пользователя.',
                                  reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(idUser, add_admin)
    elif message.text == 'Посмотреть уникальных пользователей':
        # реализовать
        return
    elif message.text == 'Посмотреть историю обращений':
        # реализовать
        return
    elif message.text == 'Вернуться':
        start_message(message)
    else:
        func = bot.send_message(message.chat.id, 'Такой функции нет, выберите заново.',
                                reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(func, select_funcAdmin)


def add_admin(message):
    # noinspection PyBroadException
    try:
        listAdmin.append(int(message.text))
        func = bot.send_message(message.chat.id, 'Успешно.',
                                reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(func, select_funcAdmin)
    except Exception:
        func = bot.send_message(message.chat.id, 'Не вышло.',
                                reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(func, select_funcAdmin)


@bot.message_handler(commands=['help'])
def help_message(message: types.Message):
    bot.send_photo(message.chat.id, photo=open('data/help.jpg', 'rb'), reply_markup=types.ReplyKeyboardRemove())
    bot.reply_to(message, "Используйте следующие команды:\n"
                          "Сделать анализ по общим пользователям - производится анализ групп VK по общим "
                          "пользователям.\n"
                          "Найти вектор комментариев - производится поиск обсуждаемых тем группы VK.\n"
                          "Для связи с поддержкой пишите сюда - @yungryouidenshi\n"
                          "/startbot - запустить бота")


@bot.message_handler(commands=['startbot'])
def start_bot(message: types.Message):
    bot.send_photo(message.chat.id, photo=open('data/work.jpg', 'rb'))
    func = bot.send_message(message.chat.id, 'Выберите функцию снизу.', reply_markup=buttons.functionalKeyboard)
    bot.register_next_step_handler(func, select_func)


def select_func(message):
    idGroupsForUsers = {}
    if message.text == buttons.butFunc1.text:
        intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор группы',
                                               reply_markup=buttons.cycleKeyboard)
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroupsForUsers)
    elif message.text == buttons.butFunc2.text:
        idGroupCom = bot.send_message(message.chat.id, 'Введите идентификатор группы',
                                      reply_markup=buttons.cycle2Keyboard)
        bot.register_next_step_handler(idGroupCom, get_comments)
    elif message.text == '/help':
        help_message(message)
    elif message.text == '/start':
        start_message(message)
    elif message.text == '/admin':
        start_admin(message)
    elif message.text == '/history':
        start_history(message)
    else:
        bot.send_message(message.chat.id, 'Такой функции нет :(')


def get_comments(message):
    global numberImageComments
    if message.text == 'Остановить':
        func = bot.send_message(message.chat.id, 'Выберите фунцию.', reply_markup=buttons.functionalKeyboard)
        bot.register_next_step_handler(func, select_func)
    else:
        # bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))
        progressMessage = bot.send_message(message.chat.id, 'Подождите, выгружаются комментарии:\n'
                                                            '[                    ] - 0%')
        comments = parserComments.get_allComments(message.text, progressMessage, bot)
        if comments == errorFoundComments:
            error = bot.send_message(message.chat.id, errorFoundComments, reply_markup=buttons.functionalKeyboard)
            bot.register_next_step_handler(error, select_func)
        elif comments == errorFoundGroup:
            error = bot.send_message(message.chat.id, errorFoundGroup, reply_markup=buttons.functionalKeyboard)
            bot.register_next_step_handler(error, select_func)
        else:
            # noinspection PyBroadException
            try:
                bot.edit_message_text('Подождите, проводится анализ: ',
                                      message.chat.id, progressMessage.message_id)
                advNumber = numberImageComments
                vectors.get_graph(comments, advNumber, progressMessage, bot)
                bot.edit_message_text('Анализ был произведён с помощью векторов слов: ',
                                      message.chat.id, progressMessage.message_id)
                bot.send_photo(message.chat.id, photo=open('picComments/' + str(advNumber) + '.png', 'rb'))
                txtFile = open('data/dataComments' + str(advNumber) + '.txt', 'r')
                bot.send_document(message.chat.id, txtFile)
                numberImageComments += 1
                bot.send_message(message.chat.id, endingFirstFunc, reply_markup=buttons.functionalKeyboard)
                bot.register_next_step_handler(message, select_func)
            except Exception:
                error = bot.send_message(message.chat.id, 'Что-то пошло не так! Заново!',
                                         reply_markup=buttons.functionalKeyboard)
                bot.register_next_step_handler(error, select_func)


def get_users(message, idGroups):
    if message.text in idGroups:
        intermediateIdGroup = bot.send_message(message.chat.id, 'Данная группа уже введена, введите новую!')
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)
    elif message.text == buttons.btnCycle1.text:
        bot.send_message(message.chat.id, 'Выберите функцию',
                         reply_markup=buttons.functionalKeyboard)
        bot.register_next_step_handler(message, select_func)
    elif message.text == buttons.btnCycle2.text and len(idGroups) < 2:
        intermediateIdGroup = bot.send_message(message.chat.id,
                                               'Групп должно быть минимум две, введите идентифактор группы!')
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)
    elif message.text == buttons.btnCycle2.text and len(idGroups) >= 2:
        get_result(message, idGroups)
    else:
        # Окей, сохраняю сообщение чтоб потом его обновлять
        progressMessage = bot.send_message(message.chat.id, 'Подождите, узнаём всех участников этой группы\n'
                                                            '[                    ] - 0%')
        parseGroup = parserUsers.check_errorFoundGroup(message.text)
        if parseGroup == errorInputGroup:
            bot.send_message(message.chat.id, errorInputGroup)
        else:
            # Мне приходится progressMessage и bot "тянуть" сквозь некоторые функции в parserUsers.py, не могу пока
            # адекватно сообразить как иначе это можно реализовать :/
            idGroups[message.text] = parserUsers.get_usersInGroup(message.text, progressMessage, bot)
        # Чтобы не плодить гигатонну сообщений построчных,
        # делаю так чтоб введённые группы выводились одним сообщением
        stringsGroups = ""
        for i in idGroups.keys():
            # Складываю названия групп
            stringsGroups += i + '\n'
        if len(stringsGroups) > 0:
            # Редактирую сообщение прогресс пара на "Введённые группы: ", ибо выведение новым сообщением
            # "Введённые группы: " и с отдельным удалением сообщения с прогресс баром выглядит некрасиво и дёрганно
            bot.edit_message_text('Введённые группы:', message.chat.id, progressMessage.message_id)
            # Вывожу список введённых групп
            bot.send_message(message.chat.id, stringsGroups)
        intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор группы')
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)


def get_result(message, idGroups):
    global numberGroupUsers

    # Не думаю что здесь нужен прогресс бар и вообще показ пикчи "паддажите",
    # ибо вывод результатов обычно невероятно быстро происходит даже
    # если пользователь ввёл много групп для анализа
    # bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))

    bot.send_message(message.chat.id, 'Общие подписчики групп: ')
    doneGroups = group.get_doneGroups(idGroups, numberGroupUsers)

    groups_intersection = group.get_groupsIntersection(doneGroups)

    # Чтобы не плодить гигатонну сообщений построчных,
    # делаю так чтоб количество общих пользователей сразу одним махом отправились
    stringsResult = ""
    for gr in groups_intersection:
        # Складываем строки
        stringsResult += (gr[0] + " и " + gr[1] + " - " + str(gr[2])
                          + " общих пользователей." + "\n")
    if len(stringsResult) > 0:
        bot.send_message(message.chat.id, stringsResult)

    bot.send_message(message.chat.id, 'Количество подписчиков: ')

    # Словарь для групп и количества членов группы
    groupsDictCountUsers = group.get_count(idGroups)
    keysGroups = groupsDictCountUsers.keys()

    # Здесь аналогично тому что было выше, обнуляем строку предварительно и опять складываем
    stringsResult = ""
    for keyGroup in keysGroups:
        # Складываем строки
        stringsResult += ("Группа " + keyGroup + " имеет " + str(groupsDictCountUsers[keyGroup])
                          + " подписчиков." + "\n")
    if len(stringsResult) > 0:
        bot.send_message(message.chat.id, stringsResult)
    # Вызываем метод передавая словари. Там затем генерируется картинка и сохраняется файлом
    advNumber = numberGroupUsers
    numberGroupUsers += 1
    graph.make_plotGraph(groupsDictCountUsers, groups_intersection, advNumber)

    # Отправляем фотку клиенту
    bot.send_photo(message.chat.id, photo=open('picUsers/' + str(advNumber) + '.png', 'rb'))
    txtFile = open('data/dataUsers' + str(advNumber) + '.txt', 'r')
    bot.send_document(message.chat.id, txtFile)
    bot.send_message(message.chat.id, endingFirstFunc, reply_markup=buttons.functionalKeyboard)
    bot.register_next_step_handler(message, select_func)


bot.infinity_polling(1)
