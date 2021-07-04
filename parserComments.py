#!/usr/bin/env python
# -*- coding: utf8 -*-
import threading
import requests
import enums
from parserPosts import ParserPosts


class ParserComments:
    token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'
    listComments = []

    def __init__(self, groupDomain, progressMessage, bot):
        self.groupDomain = groupDomain
        self.progressMessage = progressMessage
        self.bot = bot
        self.get_allComments()

    def get_response(self, offsetCount, idGroup, postId):
        return requests.get('https://api.vk.com/method/wall.getComments',
                            params={
                                'access_token': self.token,
                                'owner_id': idGroup,
                                'v': '5.131',
                                'post_id': postId,
                                'count': 100,
                                'sort': 'desc',
                                'offset': offsetCount
                            }).json()['response']

    # noinspection PyBroadException
    def get_allComments(self):
        try:
            parserPostsForId = ParserPosts(self.groupDomain)
            postsId = self.split_postsId(parserPostsForId.get_idPosts())
            idGroup = parserPostsForId.get_response(0)['items'][0]['owner_id']
            del parserPostsForId
        except Exception:
            errorFoundGroup = enums.ErrorsType.ErrorFoundGroup.value
            return errorFoundGroup

        countParsedComments = 0
        threads = list()
        # Завожу некое значение для того чтобы прогрессбар обновлялся раз в N*100 выгруженных пользователей
        refreshInterval = 50
        for post in range(0, len(postsId)):
            if countParsedComments >= 10000:
                break
            x = threading.Thread(target=self.add_comment, args=(self.listComments, 0, idGroup, postsId[post]))
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
                self.update_progress_bar(round(countParsedComments / 10000 * 100, 1))
                # Как обновили прогресс бар, обновляем значение интервала
                refreshInterval = 50
        self.update_progress_bar(100)
        [thread.join() for thread in threads]
        if len(self.listComments) == 0:
            return open('helpingFiles/ErrorFoundComments.txt').read()
        fileTime = open('data/PreviousDate.txt', 'a')
        timeNewestComment = self.get_response(0, idGroup, postsId[0])['items'][0]['date']
        fileTime.write(self.groupDomain + " " + str(timeNewestComment) + "\n")

    # noinspection PyBroadException
    def add_comment(self, listComments, offset, idGroup, postId):
        for comment in self.get_response(offset, idGroup, postId)['items']:
            try:
                listComments.append(comment['text'])
            except Exception:
                continue

    def split_postsId(self, postsId):
        listPostsId = []
        threads = list()
        for postId in postsId:
            x = threading.Thread(target=self.add_post, args=(listPostsId, postId))
            threads.append(x)
            x.start()
        [thread.join() for thread in threads]
        return listPostsId

    @staticmethod
    def add_post(listPostsId, postId):
        listPostsId.append(postId)

    # Немного костыльная дичь с проносом ProgressMessage и bot через некоторые методы парсинга,
    # если у кого есть идеи как реализовать прогресс бар лучше и с меньшим количеством костылей - напишите в конфе
    def update_progress_bar(self, percent):
        countBar = (percent // 10)
        strBarPercent = '[' + '|' * int(countBar) + ' ' * ((10 - int(countBar)) * 2) + '] - ' + str(percent) + '%'
        self.bot.edit_message_text('Подождите, выгружаются комментарии:\n' + strBarPercent,
                                   self.progressMessage.chat.id, self.progressMessage.message_id)
