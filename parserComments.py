#!/usr/bin/env python
# -*- coding: utf8 -*-
import threading
from datetime import datetime

import requests
import enums
from parserPosts import ParserPosts
from progressBar import ProgressBar


class ParserComments:
    token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'

    def __init__(self, groupDomain, progressMessage, bot, posts_comments_dates=None):
        self.groupDomain = groupDomain
        self.progressMessage = progressMessage
        self.bot = bot
        self.progressBar = ProgressBar(0, bot, progressMessage)
        if posts_comments_dates is None:
            self.listComments = self.getAllComments()
        else:
            self.posts_comments_dates = posts_comments_dates
            self.listComments = self.getActualComments()

    def getResponse(self, offsetCount, idGroup, postId):
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
    def getAllComments(self):
        try:
            parserPostsForId = ParserPosts(self.groupDomain)
            postsId = self.splitPostsId(parserPostsForId.getPosts().keys())
            postsId.sort(reverse=True)
            idGroup = parserPostsForId.getResponse(0)['items'][0]['owner_id']
            del parserPostsForId
        except Exception:
            errorFoundGroup = enums.ErrorsType.ErrorFoundGroup.value
            return errorFoundGroup

        listComments = []
        countParsedComments = 0
        threads = list()
        # Завожу некое значение для того чтобы прогрессбар обновлялся раз в N*100 выгруженных пользователей
        refreshInterval = 50
        for post in range(0, len(postsId)):
            if countParsedComments >= 10000:
                break
            x = threading.Thread(target=self.addComment, args=(listComments, 0, idGroup, postsId[post]))
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
                # WARNING! Если вдруг нужно другое количество комментариев, то придётся менять число 1500
                # Нужно как-то наверное отправлять в аргументах метода какое-нибудь поле типа maxCountParsedComments
                if round(countParsedComments / 1500 * 100, 1) > 100:
                    continue
                self.progressBar.update_progress_bar(round(countParsedComments / 1500 * 100, 1),
                                                     'Подождите, выгружаем комментарии: ')
                # Как обновили прогресс бар, обновляем значение интервала
                refreshInterval = 50
        self.progressBar.update_progress_bar(100, 'Подождите, выгружаем комментарии: ')
        [thread.join() for thread in threads]
        if len(listComments) == 0:
            return open('samplesErrors/ErrorFoundComments.txt').read()
        fileTime = open('data/newestDatesComments.txt', 'a')
        try:
            timeNewestComment = self.getResponse(0, idGroup, postsId[0])['items'][0]['date']
        except Exception:
            timeNewestComment = 0
        fileTime.write(self.groupDomain + " " + str(timeNewestComment) + "\n")
        return listComments

    # noinspection PyBroadException
    def addComment(self, listComments, offset, idGroup, postId, max_date=None):
        for comment in self.getResponse(offset, idGroup, postId)['items']:
            try:
                if max_date is not None and max_date > datetime.min and datetime.fromtimestamp(
                        comment['date']) <= max_date:
                    break

                if len(comment['text'].split()) < 3:
                    continue

                listComments.append({
                    'postId': postId,
                    'date': datetime.fromtimestamp(comment['date']),
                    'text': comment['text']
                })
            except Exception:
                continue

    def splitPostsId(self, postsId):
        listPostsId = []
        threads = list()
        for postId in postsId:
            x = threading.Thread(target=self.addPost, args=(listPostsId, postId))
            threads.append(x)
            x.start()
        [thread.join() for thread in threads]
        return listPostsId

    @staticmethod
    def addPost(listPostsId, postId):
        listPostsId.append(postId)

    def __del__(self):
        print('DeletedParserComments')

    def getActualComments(self):
        try:
            parserPostsForId = ParserPosts(self.groupDomain, max(self.posts_comments_dates.keys()))

            postsId = self.splitPostsId(parserPostsForId.getPostsSolo().keys())
            postsId.sort(reverse=True)
            idGroup = parserPostsForId.getResponse(0)['items'][0]['owner_id']
            del parserPostsForId
        except Exception:
            errorFoundGroup = enums.ErrorsType.ErrorFoundGroup.value
            return errorFoundGroup

        for postId in postsId:
            if postId not in self.posts_comments_dates:
                self.posts_comments_dates[postId] = datetime.min

        listComments = []
        countParsedComments = 0

        refreshInterval = 50
        nMax = 10000
        for post in range(0, len(postsId)):
            if countParsedComments >= nMax:
                break

            self.addComment(listComments, 0, idGroup, postsId[post], self.posts_comments_dates[postsId[post]])
            countParsedComments += 100

            if refreshInterval > 0:
                refreshInterval -= 1
                continue
            else:
                # Предотвращаем  вывод в прогресс бар значения выше 100%
                # WARNING! Если вдруг нужно другое количество комментариев, то придётся менять число 1500
                # Нужно как-то наверное отправлять в аргументах метода какое-нибудь поле типа maxCountParsedComments
                if round(countParsedComments / nMax * 100, 1) > 100:
                    continue
                self.progressBar.update_progress_bar(round(countParsedComments / nMax * 100, 1),
                                                     'Подождите, докачиваем комментарии: ')
                # Как обновили прогресс бар, обновляем значение интервала
                refreshInterval = 50
        self.progressBar.update_progress_bar(100, 'Подождите, докачиваем комментарии: ')
        if len(listComments) == 0:
            return open('samplesErrors/ErrorFoundComments.txt').read()
        fileTime = open('data/newestDatesComments.txt', 'a')
        try:
            timeNewestComment = self.getResponse(0, idGroup, postsId[0])['items'][0]['date']
        except Exception:
            timeNewestComment = 0
        fileTime.write(self.groupDomain + " " + str(timeNewestComment) + "\n")
        return listComments
