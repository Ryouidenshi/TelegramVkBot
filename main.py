from __future__ import print_function
from __future__ import unicode_literals

import gc
import types

import telebot
from telebot import types
import buttons
import enums
from graph import Graph
from group import Group
from parserUsers import ParserUsers
from vectors import Vectors
from parserComments import ParserComments

token = "1745458122:AAF4QwaORPl2ZKKGKgylhU9IQ94aJCD3sfk"

bot = telebot.TeleBot(token)

listAdmin = [402294298]

numberGroupUsers = 1

numberImageComments = 1

button = buttons.Buttons('usual')


def write_start_message(message):
    bot.reply_to(message,
                 enums.ErrorsType.Welcome.value + "\n\n"
                                                  "Используйте следующие команды:\n"
                                                  "/help - помощь\n"
                                                  "/startbot - запустить бота\n"
                                                  "/history - история запросов")


@bot.message_handler(commands=['start'])
def start_message(message: types.Message):
    global listAdmin
    bot.send_photo(message.chat.id, photo=open('data/pre.jpg', 'rb'),
                   reply_markup=button.createButton(enums.ButtonsType.RemoveButtons))
    write_start_message(message)


@bot.message_handler(commands=['history'])
def start_history(message: types.Message):
    return message
    # тут необходимо реализовать историю запросов для пользователя


@bot.message_handler(commands=['admin'])
def start_admin(message: types.Message):
    if message.from_user.id not in listAdmin:
        bot.send_message(message.chat.id, 'У вас нет прав доступа к данному разделу.',
                         reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
        start_message(message)
    else:
        f = bot.send_message(message.chat.id, 'Авторизация прошла успешно. Выберите функцию.',
                             reply_markup=button.createButton(enums.ButtonsType.AdminPanel))
        bot.register_next_step_handler(f, select_funcAdmin)


def select_funcAdmin(message):
    if message.text == enums.ButtonsType.AddAdmin.value:
        idUser = bot.send_message(message.chat.id, 'Введите id пользователя.',
                                  reply_markup=button.createButton(enums.ButtonsType.AdminPanel))
        bot.register_next_step_handler(idUser, add_admin)
    elif message.text == enums.ButtonsType.ShowCountUniqueUsers.value:
        # реализовать
        return
    elif message.text == enums.ButtonsType.ShowCountStarts.value:
        # реализовать
        return
    elif message.text == enums.ButtonsType.Back.value:
        start_message(message)
    else:
        func = bot.send_message(message.chat.id, 'Такой функции нет, выберите заново.',
                                reply_markup=button.createButton(enums.ButtonsType.AdminPanel))
        bot.register_next_step_handler(func, select_funcAdmin)


def add_admin(message):
    # noinspection PyBroadException
    try:
        listAdmin.append(int(message.text))
        func = bot.send_message(message.chat.id, 'Успешно.',
                                reply_markup=button.createButton(enums.ButtonsType.AdminPanel))
        bot.register_next_step_handler(func, select_funcAdmin)
    except Exception:
        func = bot.send_message(message.chat.id, 'Не вышло.',
                                reply_markup=button.createButton(enums.ButtonsType.AdminPanel))
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
    func = bot.send_message(message.chat.id, 'Выберите функцию снизу.',
                            reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
    bot.register_next_step_handler(func, select_func)


def select_func(message):
    idGroupsForUsers = {}
    if message.text == enums.ButtonsType.FirstFunction.value:
        intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор группы',
                                               reply_markup=button.createButton(
                                                   enums.ButtonsType.SelectFirstFunction))
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroupsForUsers)
    elif message.text == enums.ButtonsType.SecondFunction.value:
        idGroupCom = bot.send_message(message.chat.id, 'Введите идентификатор группы',
                                      reply_markup=button.createButton(enums.ButtonsType.SelectSecondFunction))
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
    if message.text == enums.ButtonsType.Stop.value:
        func = bot.send_message(message.chat.id, 'Выберите фунцию.',
                                reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(func, select_func)
    else:
        # bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))
        progressMessage = bot.send_message(message.chat.id, 'Подождите, выгружаются комментарии:\n'
                                                            '[                    ] - 0%')
        parserComments = ParserComments(message.text, progressMessage, bot)
        if parserComments.listComments == enums.ErrorsType.ErrorFoundComments.value:
            error = bot.send_message(message.chat.id, enums.ErrorsType.ErrorFoundComments.value,
                                     reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
            bot.register_next_step_handler(error, select_func)
        elif parserComments.listComments == enums.ErrorsType.ErrorFoundGroup.value:
            error = bot.send_message(message.chat.id, enums.ErrorsType.ErrorFoundGroup.value,
                                     reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
            bot.register_next_step_handler(error, select_func)
        else:
            # noinspection PyBroadException
            #try:
                bot.edit_message_text('Подождите, проводится анализ: ',
                                      message.chat.id, progressMessage.message_id)
                advNumber = numberImageComments
                vectors = Vectors(parserComments.listComments, advNumber, progressMessage, bot)
                vectors.get_graph()
                del vectors
                del parserComments
                bot.edit_message_text('Анализ был произведён с помощью векторов слов: ',
                                      message.chat.id, progressMessage.message_id)
                bot.send_photo(message.chat.id, photo=open('picComments/' + str(advNumber) + '.png', 'rb'))
                txtFile = open('data/dataComments' + str(advNumber) + '.txt', 'r')
                bot.send_document(message.chat.id, txtFile)
                numberImageComments += 1
                bot.send_message(message.chat.id, enums.ErrorsType.EndingFirstFunc.value,
                                 reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
                bot.register_next_step_handler(message, select_func)
            #except Exception:
                #error = bot.send_message(message.chat.id, 'Что-то пошло не так! Заново!',
                                         #reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
                #bot.register_next_step_handler(error, select_func)


def get_users(message, idGroups):
    if message.text in idGroups:
        intermediateIdGroup = bot.send_message(message.chat.id, 'Данная группа уже введена, введите новую!')
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)
    elif message.text == enums.ButtonsType.Stop.value:
        bot.send_message(message.chat.id, 'Выберите функцию',
                         reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(message, select_func)
    elif message.text == enums.ButtonsType.ShowResult.value and len(idGroups) < 2:
        intermediateIdGroup = bot.send_message(message.chat.id,
                                               'Групп должно быть минимум две, введите идентифактор группы!')
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)
    elif message.text == enums.ButtonsType.ShowResult.value and len(idGroups) >= 2:
        get_result(message, idGroups)
    else:
        # Окей, сохраняю сообщение чтоб потом его обновлять
        progressMessage = bot.send_message(message.chat.id, 'Подождите, узнаём всех участников этой группы\n'
                                                            '[                    ] - 0%')
        parserUsers = ParserUsers(message.text, progressMessage, bot)
        idGroups[message.text] = parserUsers.get_usersInGroup()
        stringsGroups = ""
        for i in idGroups.keys():
            stringsGroups += i + '\n'
        if len(stringsGroups) > 0:
            bot.edit_message_text('Введённые группы:', message.chat.id, progressMessage.message_id)
            bot.send_message(message.chat.id, stringsGroups)
        intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор группы')
        del parserUsers
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)


def get_result(message, idGroups):
    global numberGroupUsers

    # Не думаю что здесь нужен прогресс бар и вообще показ пикчи "паддажите",
    # ибо вывод результатов обычно невероятно быстро происходит даже
    # если пользователь ввёл много групп для анализа
    # bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))

    bot.send_message(message.chat.id, 'Общие подписчики групп: ')

    resultGroups = Group(idGroups, numberGroupUsers)

    # Чтобы не плодить гигатонну сообщений построчных,
    # делаю так чтоб количество общих пользователей сразу одним махом отправились
    stringsResult = ""
    for resultGroup in resultGroups.groupsIntersection:
        # Складываем строки
        stringsResult += (resultGroup[0] + " и " + resultGroup[1] + " - " + str(resultGroup[2])
                          + " общих пользователей." + "\n")
    if len(stringsResult) > 0:
        bot.send_message(message.chat.id, stringsResult)

    bot.send_message(message.chat.id, 'Количество подписчиков: ')

    # Словарь для групп и количества членов группы
    keysGroups = resultGroups.groups_count.keys()

    # Здесь аналогично тому что было выше, обнуляем строку предварительно и опять складываем
    stringsResult = ""
    for keyGroup in keysGroups:
        # Складываем строки
        stringsResult += ("Группа " + keyGroup + " имеет " + str(resultGroups.groups_count[keyGroup])
                          + " подписчиков." + "\n")
    if len(stringsResult) > 0:
        bot.send_message(message.chat.id, stringsResult)
    # Вызываем метод передавая словари. Там затем генерируется картинка и сохраняется файлом
    advNumber = numberGroupUsers
    numberGroupUsers += 1

    graph = Graph(resultGroups.groups_count, resultGroups.groupsIntersection, advNumber)

    graph.make_plotGraph()

    del resultGroups
    del graph

    # Отправляем фотку клиенту
    bot.send_photo(message.chat.id, photo=open('picUsers/' + str(advNumber) + '.png', 'rb'))
    txtFile = open('data/dataUsers' + str(advNumber) + '.txt', 'r')
    bot.send_document(message.chat.id, txtFile)
    bot.send_message(message.chat.id, enums.ErrorsType.EndingFirstFunc.value,
                     reply_markup=button.createButton(enums.ButtonsType.FunctionalPanel))
    bot.register_next_step_handler(message, select_func)
    gc.collect()


bot.infinity_polling(1)
