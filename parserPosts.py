import threading

import requests


class ParserPosts:
    token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'

    def __init__(self, groupDomain):
        self.groupDomain = groupDomain

    def get_response(self, offsetCount):
        return requests.get('https://api.vk.com/method/wall.get',
                            params={
                                'access_token': self.token,
                                'v': '5.131',
                                'domain': self.groupDomain,
                                'count': 100,
                                'sort': 'desc',
                                'offset': offsetCount
                            }).json()['response']

    def get_idPosts(self):
        listIdPosts = []
        response = self.get_response(0)
        maxOffset = response['count']
        offset = 0
        threads = list()
        while True:
            if offset >= maxOffset or offset >= 1000:
                break
            x = threading.Thread(target=self.add_posts, args=(listIdPosts, offset))
            offset += 100
            threads.append(x)
            x.start()
        [thread.join() for thread in threads]
        return listIdPosts

    def add_posts(self, listIdPosts, offsetCount):
        for i in self.get_response(offsetCount)['items']:
            listIdPosts.append(i['id'])

    def __del__(self):
        print('Deleted')
