from __future__ import unicode_literals
import telebot
import parserComments
import parserUsers
from telebot import types
import buttons
import group
import graph
import vectors

token = "1782563790:AAG1dhMmgZiw9_Hhzfoglxo7yRCOnwSt0jA"

bot = telebot.TeleBot(token)

welcome = open('helpingFiles/Welcome.txt').read()

endingFirstFunc = open('helpingFiles/EndFirstFunc.txt').read()

errorInputGroup = open('helpingFiles/ErrorFoundGroup.txt').read()

errorFoundComments = open('helpingFiles/ErrorFoundComments.txt').read()

errorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt').read()

listAdmin = [402294298]


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
    return
    #тут необходимо реализовать историю запросов для пользователя


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


@bot.message_handler(content_types=['text'])
def select_funcAdmin(message):
    if message.text == 'Добавить админа':
        idUser = bot.send_message(message.chat.id, 'Введите id пользователя.',
                                  reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(idUser, add_admin)
    elif message.text == 'Посмотреть уникальных пользователей':
        return
    elif message.text == 'Посмотреть историю обращений':
        return
    elif message.text == 'Вернуться':
        start_message(message)
    else:
        f = bot.send_message(message.chat.id, 'Такой функции нет, выберите заново.',
                             reply_markup=buttons.adminPanel)
        bot.register_next_step_handler(f, select_funcAdmin)


@bot.message_handler(content_types=['text'])
def add_admin(message):
    try:
        listAdmin.append(int(message.text))
        bot.send_message(message.chat.id, 'Успешно.',
                         reply_markup=buttons.adminPanel)
    except Exception:
        bot.send_message(message.chat.id, 'Не вышло.',
                         reply_markup=buttons.adminPanel)


@bot.message_handler(commands=['help'])
def help_message(message: types.Message):
    bot.send_photo(message.chat.id, photo=open('data/help.jpg', 'rb'), reply_markup=buttons.functionalKeyboard)
    bot.reply_to(message, "Используйте следующие команды:\n"
                          "Сделать анализ по общим пользователям - производится анализ групп VK по общим "
                          "пользователям.\n"
                          "Найти вектор комментариев - производится поиск обсуждаемых тем группы VK.\n"
                          "Для связи с поддержкой пишите сюда - @yungryouidenshi")


@bot.message_handler(commands=['startbot'])
def start_bot(message: types.Message):
    func = bot.send_message(message.chat.id, 'Выберите функцию снизу.', reply_markup=buttons.functionalKeyboard)
    bot.register_next_step_handler(func, select_func)


@bot.message_handler(content_types=['text'])
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


@bot.message_handler(content_types=['text'])
def get_comments(message):
    global numberImageComments
    if message.text == 'Остановить':
        func = bot.send_message(message.chat.id, 'Выберите фунцию.', reply_markup=buttons.functionalKeyboard)
        bot.register_next_step_handler(func, select_func)
    else:
        bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))
        comments = parserComments.get_allComments(message.text)
        if comments == errorFoundComments:
            error = bot.send_message(message.chat.id, errorFoundComments, reply_markup=buttons.functionalKeyboard)
            bot.register_next_step_handler(error, select_func)
        elif comments == errorFoundGroup:
            error = bot.send_message(message.chat.id, errorFoundGroup, reply_markup=buttons.functionalKeyboard)
            bot.register_next_step_handler(error, select_func)
        else:
            try:
                advNumber = numberImageComments
                bot.send_message(message.chat.id, 'Анализ был произведён с помощью векторов слов: ')
                vectors.get_graph(comments, advNumber)
                bot.send_photo(message.chat.id, photo=open('picComments/' + str(advNumber) + '.png', 'rb'))
                txtFile = open('data/dataComments' + str(advNumber) + '.txt', 'r')
                bot.send_document(message.chat.id, txtFile)
                numberImageComments += 1
                bot.send_message(message.chat.id, endingFirstFunc, reply_markup=buttons.functionalKeyboard)
            except Exception:
                error = bot.send_message(message.chat.id, 'Что-то пошло не так! Заново!',
                                         reply_markup=buttons.functionalKeyboard)
                bot.register_next_step_handler(error, select_func)


@bot.message_handler(content_types=['text'])
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
        bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))
        parseGroup = parserUsers.get_usersInGroup(message.text)
        if parseGroup == errorInputGroup:
            bot.send_message(message.chat.id, errorInputGroup)
        else:
            idGroups[message.text] = parserUsers.get_usersInGroup(message.text)
        if len(idGroups) > 0:
            bot.send_message(message.chat.id, 'Введённые группы: ')
        for i in idGroups.keys():
            bot.send_message(message.chat.id, i)
        intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор группы')
        bot.register_next_step_handler(intermediateIdGroup, get_users, idGroups)


@bot.message_handler(content_types=['text'])
def get_result(message, idGroups):
    global numberIndex
    bot.send_photo(message.chat.id, photo=open('picUsers/wait.jpg', 'rb'))
    bot.send_message(message.chat.id, 'Общие подписчики групп: ')
    doneGroups = group.get_doneGroups(idGroups, numberIndex)

    groups_intersection = group.get_groupsIntersection(doneGroups)
    for gr in groups_intersection:
        bot.send_message(message.chat.id, "Группа " + gr[0] + " и группа "
                         + gr[1] + " имеют " + str(gr[2]) + " общих пользователей.")

    bot.send_message(message.chat.id, 'Количество подписчиков: ')

    # Словарь для групп и количества членов группы
    groupsDictCountUsers = group.get_count(idGroups)
    keysGroups = groupsDictCountUsers.keys()
    for keyGroup in keysGroups:
        bot.send_message(message.chat.id, "Группа " + keyGroup + " имеет "
                         + str(groupsDictCountUsers[keyGroup]) + " подписчиков.")
    # Вызываем метод передавая словари. Там затем генерируется картинка и сохраняется файлом
    advNumber = numberIndex
    numberIndex += 1
    graph.make_plotGraph(groupsDictCountUsers, groups_intersection, advNumber)

    # Отправляем фотку клиенту
    bot.send_photo(message.chat.id, photo=open('picUsers/' + str(advNumber) + '.png', 'rb'))
    txtFile = open('data/dataUsers' + str(advNumber) + '.txt', 'r')
    bot.send_document(message.chat.id, txtFile)
    bot.send_message(message.chat.id, endingFirstFunc, reply_markup=buttons.functionalKeyboard)


numberIndex = 1

numberImageComments = 1

bot.infinity_polling(1)
