#!/usr/bin/env python
# -*- coding: utf8 -*-
import threading

import requests

import parserPosts

token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'


def get_response(offsetCount, idGroup, postId):
    return requests.get('https://api.vk.com/method/wall.getComments',
                        params={
                            'access_token': token,
                            'owner_id': idGroup,
                            'v': '5.131',
                            'post_id': postId,
                            'count': 100,
                            'sort': 'desc',
                            'offset': offsetCount
                        }).json()['response']


# noinspection PyBroadException
def get_allComments(groupDomain, progressMessage, bot, listComments=None):
    if listComments is None:
        listComments = []
    try:
        postsId = split_postsId(parserPosts.get_idPosts(groupDomain))
    except Exception:
        errorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt').read()
        return errorFoundGroup
    idGroup = parserPosts.get_response(0, groupDomain)['items'][0]['owner_id']

    countParsedComments = 0
    threads = list()
    # Завожу некое значение для того чтобы прогрессбар обновлялся раз в N*100 выгруженных пользователей
    refreshInterval = 50
    for post in range(0, len(postsId)):
        if countParsedComments >= 10000:
            break
        x = threading.Thread(target=add_comment, args=(listComments, 0, idGroup, postsId[post]))
        threads.append(x)
        x.start()
        countParsedComments += 100
        # Если значение всё ещё положительное (то есть ещё не выгрузили N*1000 пользователей из группы),
        # прогресс бар не трогаем и просто продолжаем выгружать
        if refreshInterval > 0:
            refreshInterval -= 1
            continue
        else:
            # Предотвращаем  вывод в прогресс бар значения выше 100%
            # WARNING! Если вдруг нужно другое количество комментариев, то придётся менять число 10000
            # Нужно как-то наверное отправлять в аргументах метода какое-нибудь поле типа maxCountParsedComments
            if round(countParsedComments / 10000 * 100, 1) > 100:
                continue
            update_progress_bar(round(countParsedComments / 10000 * 100, 1), progressMessage, bot)
            # Как обновили прогресс бар, обновляем значение интервала
            refreshInterval = 50
    update_progress_bar(100, progressMessage, bot)
    [thread.join() for thread in threads]
    if len(listComments) == 0:
        return open('helpingFiles/ErrorFoundComments.txt').read()
    fileTime = open('data/PreviousDate.txt', 'a')
    timeNewestComment = get_response(0, idGroup, postsId[0])['items'][0]['date']
    fileTime.write(groupDomain + " " + str(timeNewestComment) + "\n")
    return listComments


# noinspection PyBroadException
def add_comment(listComments, offset, idGroup, postId):
    for comment in get_response(offset, idGroup, postId)['items']:
        try:
            listComments.append(comment['text'])
        except Exception:
            continue


def split_postsId(postsId, listPostsId=None):
    if listPostsId is None:
        listPostsId = []
    threads = list()
    for postId in postsId:
        x = threading.Thread(target=add_post, args=(listPostsId, postId))
        threads.append(x)
        x.start()
    [thread.join() for thread in threads]
    return listPostsId


def add_post(listPostsId, postId):
    listPostsId.append(postId)


# Немного костыльная дичь с проносом ProgressMessage и bot через некоторые методы парсинга,
# если у кого есть идеи как реализовать прогресс бар лучше и с меньшим количеством костылей - напишите в конфе
def update_progress_bar(percent, message, bot):
    countBar = (percent // 10)
    strBarPercent = '[' + '|' * int(countBar) + ' ' * ((10 - int(countBar)) * 2) + '] - ' + str(percent) + '%'
    bot.edit_message_text('Подождите, выгружаются комментарии:\n' + strBarPercent,
                          message.chat.id, message.message_id)
