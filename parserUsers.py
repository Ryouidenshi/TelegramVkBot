import threading
import requests

import enums


class ParserUsers:
    token = '74414b0d74414b0d74414b0d51743900907744174414b0d148cb840b3a4c7c908271c3d'

    def __init__(self, groupId, progressMessage, bot):
        self.groupId = groupId
        self.progressMessage = progressMessage
        self.bot = bot

    def get_response(self, offsetCount, groupId):
        return requests.get('https://api.vk.com/method/groups.getMembers',
                            params={
                                'access_token': self.token,
                                'v': '5.131',
                                'group_id': groupId,
                                'sort': 'id_desc',
                                'offset': offsetCount,
                                'fields': 'last_seen'
                            }).json()['response']

    def get_resp(self):
        # Завожу некое значение для того чтобы прогрессбар обновлялся раз в N*1000 выгруженных пользователей
        refreshInterval = 100
        listResponses = []
        offset = 0
        maxOffset = self.get_response(0, self.groupId)['count']
        threads = list()
        while True:
            if offset > maxOffset:
                break
            x = threading.Thread(target=self.get_threadResp, args=(listResponses, offset, self.groupId))
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
                self.update_progress_bar(round(offset / maxOffset * 100, 1), self.progressMessage, self.bot)
                # Как обновили прогресс бар, обновляем значение интервала
                refreshInterval = 100
        self.update_progress_bar(100, self.progressMessage, self.bot)
        [thread.join() for thread in threads]
        threads.clear()
        return listResponses

    def get_threadResp(self, listResponses, offset, groupId):
        listResponses.append(self.get_response(offset, groupId))

    # noinspection PyBroadException
    def get_usersInGroup(self, listUsersInGroup=None):
        if listUsersInGroup is None:
            listUsersInGroup = []
        try:
            responses = self.get_resp()
            for response in responses:
                for item in response['items']:
                    listUsersInGroup.append(item['id'])
            return listUsersInGroup
        except Exception:
            return enums.ErrorsType.ErrorFoundGroup.value

    # Немного костыльная дичь с проносом ProgressMessage и bot через некоторые методы парсинга,
    # если у кого есть идеи как реализовать прогресс бар лучше и с меньшим количеством костылей - напишите в конфе
    @staticmethod
    def update_progress_bar(percent, message, bot):
        countBar = (percent // 10)
        strBarPercent = '[' + '|' * int(countBar) + ' ' * ((10 - int(countBar)) * 2) + '] - ' + str(percent) + '%'
        bot.edit_message_text('Подождите, узнаём всех участников этой группы\n' + strBarPercent,
                              message.chat.id, message.message_id)

    def __del__(self):
        print('Deleted')
