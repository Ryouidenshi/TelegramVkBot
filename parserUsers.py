import threading

import requests

errorInputGroupForFindUsers = open('helpingFiles/ErrorFoundGroup.txt').read()

token = '74414b0d74414b0d74414b0d51743900907744174414b0d148cb840b3a4c7c908271c3d'


def get_response(offsetCount, groupId):
    return requests.get('https://api.vk.com/method/groups.getMembers',
                        params={
                            'access_token': token,
                            'v': '5.131',
                            'group_id': groupId,
                            'sort': 'id_desc',
                            'offset': offsetCount,
                            'fields': 'last_seen'
                        }).json()['response']


def get_resp(groupId, progressMessage, bot, listResponses=None):
    # Завожу некое значение для того чтобы прогрессбар обновлялся раз в N*1000 выгруженных пользователей
    refreshInterval = 100
    if listResponses is None:
        listResponses = []
    offset = 0
    maxOffset = get_response(0, groupId)['count']
    threads = list()
    while True:
        if offset > maxOffset:
            break
        x = threading.Thread(target=get_threadResp, args=(listResponses, offset, groupId))
        offset += 1000
        threads.append(x)
        x.start()
        # Если значение всё ещё положительное (то есть ещё не выгрузили N*1000 пользователей из группы),
        # прогресс бар не трогаем и просто продолжаем выгружать
        if refreshInterval > 0:
            refreshInterval -= 1
            continue
        else:
            # Предотвращаем  вывод в прогресс бар значения выше 100%,
            # ибо offset в каких-то случаях может оказаться больше maxOffset
            if round(offset / maxOffset * 100, 1) > 100:
                continue
            update_progress_bar(round(offset / maxOffset * 100, 1), progressMessage, bot)
            # Как обновили прогресс бар, обновляем значение интервала
            refreshInterval = 100
    update_progress_bar(100, progressMessage, bot)
    [thread.join() for thread in threads]
    return listResponses


def get_threadResp(listResponses, offset, groupId):
    listResponses.append(get_response(offset, groupId))


def get_usersInGroup(groupId, progressMessage, bot, listUsersInGroup=None):
    if listUsersInGroup is None:
        listUsersInGroup = []
    try:
        responses = get_resp(groupId, progressMessage, bot)
        for response in responses:
            for item in response['items']:
                listUsersInGroup.append(item['id'])
        return listUsersInGroup
    except Exception:
        errorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt').read()
        return errorFoundGroup


def check_errorFoundGroup(groupId):
    try:
        get_response(0, groupId)
    except Exception:
        errorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt').read()
        return errorFoundGroup


# Немного костыльная дичь с проносом ProgressMessage и bot через некоторые методы парсинга,
# если у кого есть идеи как реализовать прогресс бар лучше и с меньшим количеством костылей - напишите в конфе
def update_progress_bar(percent, message, bot):
    countBar = (percent // 10)
    strBarProcent = '[' + '|' * int(countBar) + ' ' * ((10 - int(countBar)) * 2) + '] - ' + str(percent) + '%'
    bot.edit_message_text('Подождите, узнаём всех участников этой группы\n' + strBarProcent,
                          message.chat.id, message.message_id)
