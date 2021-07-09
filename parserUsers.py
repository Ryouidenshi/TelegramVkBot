import threading
import requests

import enums
from progressBar import ProgressBar


class ParserUsers:
    token = '74414b0d74414b0d74414b0d51743900907744174414b0d148cb840b3a4c7c908271c3d'

    def __init__(self, groupId, progressMessage, bot):
        self.groupId = groupId
        self.progressMessage = progressMessage
        self.bot = bot
        self.progressBar = ProgressBar(0, bot, progressMessage)

    def getResponse(self, offsetCount, groupId):
        return requests.get('https://api.vk.com/method/groups.getMembers',
                            params={
                                'access_token': self.token,
                                'v': '5.131',
                                'group_id': groupId,
                                'sort': 'id_desc',
                                'offset': offsetCount
                            }).json()['response']

    def getResp(self):
        # Завожу некое значение для того чтобы прогрессбар обновлялся раз в N*1000 выгруженных пользователей
        refreshInterval = 100
        listResponses = []
        offset = 0
        maxOffset = self.getResponse(0, self.groupId)['count']
        threads = list()
        while True:
            if offset > maxOffset:
                break
            x = threading.Thread(target=self.getThreadResp, args=(listResponses, offset, self.groupId))
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
                if round(offset / maxOffset * 100, 1) > 80:
                    continue
                self.progressBar.update_progress_bar(round(offset / maxOffset * 100, 1),
                                                     'Подождите, идёт загрузка участников группы:')
                # Как обновили прогресс бар, обновляем значение интервала
                refreshInterval = 100
        [thread.join() for thread in threads]
        threads.clear()
        return listResponses

    def getThreadResp(self, listResponses, offset, groupId):
        listResponses.append(self.getResponse(offset, groupId))

    # noinspection PyBroadException
    def getUsersInGroup(self, listUsersInGroup=None):
        if listUsersInGroup is None:
            listUsersInGroup = []
        try:
            responses = self.getResp()
            for response in responses:
                for item in response['items']:
                    listUsersInGroup.append(item)
            return listUsersInGroup
        except Exception:
            return enums.ErrorsType.ErrorFoundGroup.value

    def checkGroup(self, listUsersInGroup=None):
        if listUsersInGroup is None:
            listUsersInGroup = []
        # noinspection PyBroadException
        try:
            responses = [self.getResponse(0, self.groupId)]
            for response in responses:
                for item in response['items']:
                    listUsersInGroup.append(item)
            return listUsersInGroup
        except Exception:
            return enums.ErrorsType.ErrorFoundGroup.value

    def __del__(self):
        print('Deleted')
