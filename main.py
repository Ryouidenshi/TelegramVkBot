from __future__ import print_function
from __future__ import unicode_literals
import os
import types
import telebot
from telebot import types
import buttons
import db_queries
import re
import enums
from attendanceGraph import AttendanceGraph
from graphUsers import Graph
from groups import Groups
from parserUsers import ParserUsers
from commentVectors import CommentVectors
from parserComments import ParserComments

token = "1745458122:AAF4QwaORPl2ZKKGKgylhU9IQ94aJCD3sfk"

bot = telebot.TeleBot(token)

allButtons = buttons.Buttons()


def write_start_message(message):
    bot.reply_to(message,
                 enums.ErrorsType.Welcome.value + "\n\n"
                                                  "Используйте следующие команды:\n"
                                                  "/help - помощь\n"
                                                  "/startbot - запустить бота\n"
                                                  "/history - история запросов")


@bot.message_handler(commands=['start'])
def start_message(message: types.Message):
    bot.send_photo(message.chat.id, photo=open('picturesForMenu/pre.jpg', 'rb'),
                   reply_markup=allButtons.createButton(enums.ButtonsType.RemoveButtons))
    db_queries.add_query(message.from_user.id, 'start')
    write_start_message(message)


@bot.message_handler(commands=['help'])
def help_message(message: types.Message):
    bot.send_photo(message.chat.id, photo=open('picturesForMenu/help.jpg', 'rb'),
                   reply_markup=types.ReplyKeyboardRemove())
    bot.reply_to(message, "Используйте следующие команды:\n"
                          "Сделать анализ по общим пользователям - производится анализ групп VK по общим "
                          "пользователям.\n"
                          "Найти вектор комментариев - производится поиск обсуждаемых тем группы VK.\n"
                          "Для связи с поддержкой пишите сюда - @yungryouidenshi\n"
                          "/startbot - запустить бота")
    db_queries.add_query(message.from_user.id, 'help')


@bot.message_handler(commands=['history'])
def start_history(message: types.Message):
    db_queries.add_query(message.from_user.id, 'history')
    historyData = db_queries.get_history(message.from_user.id)
    if len(historyData) == 0:
        bot.send_message(message.chat.id, 'История запросов пуста')
    else:
        stringHistory = "История Ваших запросов: " + '\n\n'
        for row in historyData:
            stringHistory += "[" + str(row[0]) + "]: " + row[1] + '\n'
        bot.send_message(message.chat.id, stringHistory)


@bot.message_handler(commands=['admin', 'moderator'])
def start_privilege(message: types.Message):
    if message.text == '/admin' and message.from_user.id not in db_queries.get_roles()["admin"] \
            or message.text == '/moderator' and message.from_user.id not in db_queries.get_roles()["moder"]:
        bot.send_message(message.chat.id, 'У Вас нет прав доступа к данному разделу.',
                         reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
        start_message(message)
        db_queries.add_query(message.from_user.id, 'admin_try')
    else:
        doneEntry = bot.send_message(message.chat.id, 'Авторизация прошла успешно. Выберите функцию.',
                                     reply_markup=allButtons.createButton(enums.ButtonsType.AdminPanel))
        db_queries.add_query(message.from_user.id, 'admin_login')
        bot.register_next_step_handler(doneEntry, select_funcPrivilege)


def select_funcPrivilege(message):
    if message.text == enums.ButtonsType.AddModerator.value:
        if message.from_user.id in db_queries.get_roles()["admin"]:
            idUser = bot.send_message(message.chat.id, 'Введите id пользователя.',
                                      reply_markup=allButtons.createButton(enums.ButtonsType.Stop))
            bot.register_next_step_handler(idUser, add_moderator)
        else:
            messageErrorAddModerator = bot.send_message(message.chat.id,
                                                        'У вас недостаточно прав для этого действия!',
                                                        reply_markup=allButtons.createButton(
                                                            enums.ButtonsType.AdminPanel))
            bot.register_next_step_handler(messageErrorAddModerator, select_funcPrivilege)
    elif message.text == enums.ButtonsType.ShowUniqueUsers.value:
        sumUniqueUsers = 0
        db_queries.add_query(message.from_user.id, 'view_unique')
        unique_users = db_queries.get_users(unique=True)
        unique_users_string = "Информация об уникальных пользователях:" + '\n\n'
        for data in unique_users:
            unique_users_string += "[" + str(data["date"]) + "]: " + str(data["counts"]) + '\n'
            sumUniqueUsers += data['counts']
        uniqueUsers = bot.send_message(message.chat.id, unique_users_string)
        AttendanceGraph(unique_users).get_graph_unique_users()
        bot.send_photo(message.chat.id, photo=open('data/countUniqueUsers.png', 'rb'))
        bot.send_message(message.chat.id, 'Общее количество уникальных пользователей - ' + str(sumUniqueUsers))
        bot.register_next_step_handler(uniqueUsers, select_funcPrivilege)
    elif message.text == enums.ButtonsType.ShowCountStarts.value:
        sumCountStarts = 0
        db_queries.add_query(message.from_user.id, 'admin_history')
        countsStarts = db_queries.get_users()
        unique_users_string = "Информация о посещениях:" + '\n\n'
        for data in countsStarts:
            unique_users_string += "[" + str(data["date"]) + "]: " + str(data["counts"]) + '\n'
            sumCountStarts += data['counts']
        countsStartsMessage = bot.send_message(message.chat.id, unique_users_string)
        AttendanceGraph(countsStarts).get_graph_counts_starts()
        bot.send_photo(message.chat.id, photo=open('data/countsStarts.png', 'rb'))
        bot.send_message(message.chat.id, 'Общее количество использований - ' + str(sumCountStarts))
        bot.register_next_step_handler(countsStartsMessage, select_funcPrivilege)
    elif message.text == enums.ButtonsType.Back.value:
        start_message(message)
    else:
        func = bot.send_message(message.chat.id, 'Такой функции нет, выберите заново.',
                                reply_markup=allButtons.createButton(enums.ButtonsType.AdminPanel))
        bot.register_next_step_handler(func, select_funcPrivilege)


def add_moderator(message):
    if message.text == enums.ButtonsType.Stop.value:
        funcAdmin = bot.send_message(message.chat.id, 'Выберите функцию.',
                                     reply_markup=allButtons.createButton(enums.ButtonsType.AdminPanel))
        bot.register_next_step_handler(funcAdmin, select_funcPrivilege)
    else:
        # noinspection PyBroadException
        try:
            db_queries.add_moder(message.text)
            funcAdmin = bot.send_message(message.chat.id, 'Успешно.',
                                         reply_markup=allButtons.createButton(enums.ButtonsType.AdminPanel))
            bot.register_next_step_handler(funcAdmin, select_funcPrivilege)
            db_queries.add_query(message.from_user.id, 'add_admin')
        except Exception:
            funcAdmin = bot.send_message(message.chat.id, 'Не вышло.',
                                         reply_markup=allButtons.createButton(enums.ButtonsType.AdminPanel))
            bot.register_next_step_handler(funcAdmin, select_funcPrivilege)


@bot.message_handler(commands=['startbot'])
def start_bot(message: types.Message):
    bot.send_photo(message.chat.id, photo=open('picturesForMenu/work.jpg', 'rb'))
    func = bot.send_message(message.chat.id, 'Выберите функцию снизу.',
                            reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
    bot.register_next_step_handler(func, select_func)


def select_func(message):
    idGroupsForUsers = {}
    if message.text == enums.ButtonsType.FirstFunction.value:
        intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор своей группы',
                                               reply_markup=allButtons.createButton(
                                                   enums.ButtonsType.SelectFirstFunction))
        bot.register_next_step_handler(intermediateIdGroup, get_users_in_group, idGroupsForUsers)

    elif message.text == enums.ButtonsType.SecondFunction.value:
        idGroupCom = bot.send_message(message.chat.id, 'Введите идентификатор группы',
                                      reply_markup=allButtons.createButton(enums.ButtonsType.SelectSecondFunction))
        bot.register_next_step_handler(idGroupCom, get_comments)

    elif message.text == enums.ButtonsType.Favorite.value:
        myFavorites = db_queries.get_my_favorite(message.from_user.id)
        if len(myFavorites) == 0:
            bot.send_message(message.chat.id, 'Ваш список избранных групп пуст')
            func = bot.send_message(message.chat.id, 'Выберите функцию снизу.',
                                    reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
            bot.register_next_step_handler(func, select_func)
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            for row in myFavorites:
                keyboard.add("[ID " + str(row[0]) + ", " + str(row[1]) + "] " + row[2])

            keyboard.add(enums.ButtonsType.Back.value)
            func = bot.send_message(chat_id=message.chat.id,
                                    text="Выберите один из элементов избранных групп",
                                    reply_markup=keyboard
                                    )
            bot.register_next_step_handler(func, selected_favorite)
        db_queries.add_query(message.from_user.id, 'favorites')

    elif message.text == '/help':
        help_message(message)
    elif message.text == '/start':
        start_message(message)
    elif message.text == '/admin':
        start_privilege(message)
    elif message.text == '/history':
        start_history(message)
    else:
        message = bot.send_message(message.chat.id, 'Такой функции нет :(')
        bot.register_next_step_handler(message, select_func)


def get_comments_list(message):
    progressMessage = bot.send_message(message.chat.id, 'Подождите, выгружаются комментарии:\n'
                                                        '[                    ] - 0%')
    parserComments = ParserComments(message.text, progressMessage, bot)
    listComments = parserComments.listComments
    return listComments


def get_comments(message):
    if message.text == enums.ButtonsType.Stop.value:
        func = bot.send_message(message.chat.id, 'Выберите фунцию.',
                                reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(func, select_func)
    else:

        group_data = db_queries.get_group_data(message.text)
        group_id = group_data['id']
        last_comment = group_data['last_comment_date']
        comments_data_from_db = db_queries.get_comments_data(group_id)

        if len(comments_data_from_db['listComments']) == 0:
            listComments = get_comments_list(message)
            if listComments == enums.ErrorsType.ErrorFoundGroup.value:
                error = bot.send_message(message.chat.id, enums.ErrorsType.ErrorFoundGroup.value
                                         , reply_markup=buttons.Buttons.createButton(enums.ButtonsType.FunctionalPanel))
                bot.register_next_step_handler(error, select_func)
            elif listComments == enums.ErrorsType.ErrorFoundComments.value:
                error = bot.send_message(message.chat.id, enums.ErrorsType.ErrorFoundComments.value
                                         , reply_markup=buttons.Buttons.createButton(enums.ButtonsType.FunctionalPanel))
                bot.register_next_step_handler(error, select_func)
            else:
                db_queries.insert_comments_data(group_id, listComments)

                onlyCommentsList = []
                for row in listComments:
                    onlyCommentsList.append(row['text'])
                maxComments = len(onlyCommentsList) if len(onlyCommentsList) < 10000 else 10000
                if maxComments < 10:
                    error = bot.send_message(message.chat.id, 'В группе недостаточно комментариев для анализа'
                                             , reply_markup=buttons.Buttons.
                                             createButton(enums.ButtonsType.FunctionalPanel))
                    bot.register_next_step_handler(error, select_func)
                else:
                    countNeededComments = bot.send_message(message.chat.id, 'Введите нужное количество комментариев.\n'
                                                           + 'Максимум - ' + str(maxComments) + '\n'
                                                           + 'Минимум - 10',
                                                           reply_markup=buttons.Buttons.createButton(
                                                               enums.ButtonsType.Stop))
                    bot.register_next_step_handler(countNeededComments, analyze_comments, onlyCommentsList)
        else:
            actualOrUpdated = bot.send_message(message.chat.id,
                                               'В нашей базе имеются комментарии данного сообщества (' + str(
                                                   len(comments_data_from_db['listComments'])) + ' шт.), ' +
                                               'дата последнего комментария – ' + str(
                                                   last_comment) +
                                               ', актуализировать данные или использовать имеющиеся комментарии?',
                                               reply_markup=allButtons.createButton(enums.ButtonsType.ActualButtons))
            bot.register_next_step_handler(actualOrUpdated, select_comments_type, group_id, message.text,
                                           comments_data_from_db['listComments'])


def get_users_in_group(message, idGroups):
    if message.text in idGroups:
        intermediateIdGroup = bot.send_message(message.chat.id, 'Данная группа уже введена, введите новую!')
        bot.register_next_step_handler(intermediateIdGroup, get_users_in_group, idGroups)
    elif message.text == enums.ButtonsType.Stop.value:
        func = bot.send_message(message.chat.id, 'Выберите функцию',
                                reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(func, select_func)
    elif message.text == enums.ButtonsType.ShowResult.value and len(idGroups) < 2:
        intermediateIdGroup = bot.send_message(message.chat.id,
                                               'Групп должно быть минимум две, введите идентифактор группы!')
        bot.register_next_step_handler(intermediateIdGroup, get_users_in_group, idGroups)
    elif message.text == enums.ButtonsType.ShowResult.value and len(idGroups) >= 2:
        get_information_about_groups(message, idGroups)
    else:
        # Окей, сохраняю сообщение чтоб потом его обновлять
        progressMessage = bot.send_message(message.chat.id, 'Подождите, узнаём всех участников этой группы\n'
                                                            '[                    ] - 0%')
        parserUsers = ParserUsers(message.text, progressMessage, bot)
        if parserUsers.checkGroup() == enums.ErrorsType.ErrorFoundGroup.value:
            someGroup = bot.send_message(message.chat.id, 'Группа не найдена, введите другую!')
            bot.register_next_step_handler(someGroup, get_users_in_group, idGroups)
        else:
            group_data_from_db = db_queries.get_group_data_users(message.text)
            if group_data_from_db == 0:
                idGroups[message.text] = parserUsers.getUsersInGroup()
                db_queries.insert_group_data(message.text, idGroups[message.text])
                bot.edit_message_text('Подождите, выгружаются комментарии:\n[||||||||||] - 100%',
                                      progressMessage.chat.id, progressMessage.message_id)
            else:
                idGroups[message.text] = group_data_from_db

            stringsGroups = ""
            for i in idGroups.keys():
                stringsGroups += i + '\n'
            if len(stringsGroups) > 0:
                bot.edit_message_text('Введённые группы:', message.chat.id, progressMessage.message_id)
                bot.send_message(message.chat.id, stringsGroups)
            intermediateIdGroup = bot.send_message(message.chat.id, 'Введите идентификатор другой группы')
            del parserUsers
            bot.register_next_step_handler(intermediateIdGroup, get_users_in_group, idGroups)


def get_information_about_groups(message, idGroups, isFavorite=0):
    # Не думаю что здесь нужен прогресс бар и вообще показ пикчи "паддажите",
    # ибо вывод результатов обычно невероятно быстро происходит даже
    # если пользователь ввёл много групп для анализа

    requestNumberUsers = len(os.listdir(path="dataUsers")) + 1
    requestNumberUsers = message.from_user.username + 'Users' + str(requestNumberUsers)
    bot.send_message(message.chat.id, 'Общие подписчики групп: ')

    resultGroups = Groups(idGroups, requestNumberUsers)

    # Чтобы не плодить гигатонну сообщений построчных,
    # делаю так чтоб количество общих пользователей сразу одним махом отправились
    stringsResult = ""
    for resultGroup in resultGroups.groupsIntersection:
        # Складываем строки
        stringsResult += (resultGroup[0] + " и " + resultGroup[1] + " - " + str(resultGroup[2])
                          + " общих пользователей." + "\n")
    if len(stringsResult) > 0:
        bot.send_message(message.chat.id, stringsResult)
    group_history_id = db_queries.add_groups_to_history(message.from_user.id, idGroups.keys())

    bot.send_message(message.chat.id, 'Количество подписчиков: ')

    # Словарь для групп и количества членов группы
    keysGroups = resultGroups.getCountsUsersInGroups.keys()

    # Здесь аналогично тому что было выше, обнуляем строку предварительно и опять складываем
    stringsResult = ""
    for keyGroup in keysGroups:
        # Складываем строки
        stringsResult += ("Группа " + keyGroup + " имеет " + str(resultGroups.getCountsUsersInGroups[keyGroup])
                          + " подписчиков." + "\n")
    if len(stringsResult) > 0:
        bot.send_message(message.chat.id, stringsResult)
    # Вызываем метод передавая словари. Там затем генерируется картинка и сохраняется файлом
    graph = Graph(resultGroups.getCountsUsersInGroups, resultGroups.groupsIntersection, requestNumberUsers)

    graph.makePlotGraph()
    resultGroups.getFileTxt()

    del resultGroups
    del graph

    # Отправляем фотку клиенту
    bot.send_photo(message.chat.id, photo=open('graphsUsers/' + str(requestNumberUsers) + '.png', 'rb'))
    txtFile = open('dataUsers/' + str(requestNumberUsers) + '.txt', 'r')
    bot.send_document(message.chat.id, txtFile)

    bot.send_message(message.chat.id, enums.ErrorsType.EndingFirstFunc.value,
                     reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))

    db_queries.add_query(message.from_user.id, 'groups')
    if isFavorite == 0:
        bot.send_message(message.chat.id, "Добавить группы в избранное для дальнейшего быстрого доступа?",
                         reply_markup=allButtons.createButton(enums.ButtonsType.YesOrNo))
        bot.register_next_step_handler(message, add_groups_to_favorite, group_history_id)
    else:
        func = bot.send_message(message.chat.id, 'Выберите функцию',
                                reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(func, select_func)


def add_groups_to_favorite(message, group_history_id):
    if message.text == enums.ButtonsType.Yes.value:
        db_queries.set_groups_favorite(group_history_id)
    bot.send_message(message.chat.id, enums.ErrorsType.EndingFirstFunc.value,
                     reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
    bot.register_next_step_handler(message, select_func)


def selected_favorite(message):
    if message.text == enums.ButtonsType.Back.value:
        start_bot(message)
    else:

        favoriteId = re.search(r'\d+', r'' + message.text + '').group(0)
        favoriteData = db_queries.get_favorite_groups(message.from_user.id, favoriteId)

        if favoriteData == 0:
            bot.send_message(message.chat.id, 'Неизвестный элемент избранного')

        else:
            idGroups = {}
            for group in favoriteData.split(","):
                dataFav = db_queries.get_group_data_users(group)
                if dataFav != 0:
                    idGroups[group] = dataFav
                else:
                    progressMessage = bot.send_message(message.chat.id,
                                                       'Подождите, актуализируем данные\n'
                                                       '[                    ] - 0%')
                    parserUsers = ParserUsers(group, progressMessage, bot)
                    idGroups[group] = parserUsers.getUsersInGroup()
                    db_queries.insert_group_data(message.text, idGroups[group])

                    bot.edit_message_text('Подождите, догружаем комментарии:\n[||||||||||] - 100%',
                                          progressMessage.chat.id, progressMessage.message_id)

                    bot.delete_message(message.chat.id, progressMessage.message_id)
            get_information_about_groups(message, idGroups, 1)


def select_comments_type(message, group_id, group_domain, listComments):
    if message.text == enums.ButtonsType.GetActual.value:
        posts_comments_dates = db_queries.get_posts_comments_dates(group_id)
        progressMessage = bot.send_message(message.chat.id, 'Подождите, выгружаются комментарии:\n' +
                                           '[                    ] - 0%')
        parserComments = ParserComments(group_domain, progressMessage, bot, posts_comments_dates)

        if len(parserComments.listComments) > 0:
            added = db_queries.insert_comments_data(group_id, parserComments.listComments)
            onlyCommentsList = db_queries.get_comments_data(group_id)['listComments']
            bot.send_message(message.chat.id, 'Докачано ' + str(added) + ' комментариев')
        else:
            onlyCommentsList = listComments
            bot.send_message(message.chat.id, 'Оказалось, что докачивать нечего')

        maxComments = len(onlyCommentsList) if len(onlyCommentsList) < 10000 else 10000
        countNeededComments = bot.send_message(message.chat.id, 'Введите нужное количество комментариев.\n'
                                               + 'Максимум - ' + str(maxComments) + '\n'
                                               + 'Минимум - 10',
                                               reply_markup=buttons.Buttons.createButton(enums.ButtonsType.Stop))
        bot.register_next_step_handler(countNeededComments, analyze_comments, listComments)

    elif message.text == enums.ButtonsType.UseExists.value:
        maxComments = len(listComments) if len(listComments) < 10000 else 10000
        countNeededComments = bot.send_message(message.chat.id, 'Введите нужное количество комментариев.\n'
                                               + 'Максимум - ' + str(maxComments) + '\n'
                                               + 'Минимум - 10',
                                               reply_markup=buttons.Buttons.createButton(enums.ButtonsType.Stop))
        bot.register_next_step_handler(countNeededComments, analyze_comments, listComments)


def analyze_comments(message, listComments):
    try:
        if message.text == enums.ButtonsType.Stop.value:
            stop = bot.send_message(message.chat.id, 'Выберите функцию.',
                                    reply_markup=buttons.Buttons.createButton(
                                        enums.ButtonsType.FunctionalPanel))
            bot.register_next_step_handler(stop, select_func)
        elif int(message.text) > len(listComments) or int(message.text) > 10000 \
                or int(message.text) <= 0 or int(message.text) <= 10:
            error = bot.send_message(message.chat.id, 'Данное количество анализировать нельзя!',
                                     reply_markup=buttons.Buttons.createButton(enums.ButtonsType.FunctionalPanel))
            bot.register_next_step_handler(error, select_func)
        else:
            if listComments == enums.ErrorsType.ErrorFoundComments.value:
                error = bot.send_message(message.chat.id, enums.ErrorsType.ErrorFoundComments.value,
                                         reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
                bot.register_next_step_handler(error, select_func)
            elif listComments == enums.ErrorsType.ErrorFoundGroup.value:
                error = bot.send_message(message.chat.id, enums.ErrorsType.ErrorFoundGroup.value,
                                         reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
                bot.register_next_step_handler(error, select_func)
            else:
                get_analyze(message, listComments)
    except ValueError:
        error = bot.send_message(message.chat.id, 'Некорректный ввод.',
                                 reply_markup=buttons.Buttons.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(error, select_func)


def get_analyze(message, listComments):
    # noinspection PyBroadException
    try:
        progressMessage = bot.send_message(message.chat.id, 'Подождите, проводится анализ')
        requestNumberComments = len(os.listdir(path="dataComments")) + 1

        advNumber = message.from_user.username + 'Comments' + str(requestNumberComments)
        requestNumberComments += 1
        vectors = CommentVectors(listComments, advNumber, progressMessage, bot, int(message.text))
        vectors.getGraph()
        del vectors

        bot.edit_message_text('Анализ был произведён с помощью векторов слов: ',
                              message.chat.id, progressMessage.message_id)
        bot.send_photo(message.chat.id, photo=open('graphsComments/' + str(advNumber) + '.png', 'rb'))
        txtFile = open('dataComments/' + str(advNumber) + '.txt', 'r')
        bot.send_document(message.chat.id, txtFile)
        bot.send_message(message.chat.id, enums.ErrorsType.EndingFirstFunc.value,
                         reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(message, select_func)
        db_queries.add_query(message.from_user.id, 'comments')
    except Exception:
        error = bot.send_message(message.chat.id, 'Что-то пошло не так! Возможно вы ввели неккоректно данные.',
                                 reply_markup=allButtons.createButton(enums.ButtonsType.FunctionalPanel))
        bot.register_next_step_handler(error, select_func)


bot.infinity_polling(1)
