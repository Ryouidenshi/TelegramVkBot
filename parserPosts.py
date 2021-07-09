import threading

import requests


class ParserPosts:
    token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'

    def __init__(self, groupDomain, last=False):
        self.groupDomain = groupDomain
        self.last = last

    def getResponse(self, offsetCount):
        return requests.get('https://api.vk.com/method/wall.get',
                            params={
                                'access_token': self.token,
                                'v': '5.131',
                                'domain': self.groupDomain,
                                'count': 100,
                                'sort': 'desc',
                                'offset': offsetCount
                            }).json()['response']

    def getPosts(self):
        posts = {}
        response = self.getResponse(0)
        maxOffset = response['count']
        offset = 0
        threads = list()
        while True:
            if offset >= maxOffset or offset >= 10000:
                break
            x = threading.Thread(target=self.addPosts, args=(posts, offset))
            offset += 100
            threads.append(x)
            x.start()

            if self.last is not None and self.last in posts:
                break

        [thread.join() for thread in threads]
        return posts

    def getPostsSolo(self):
        posts = {}
        response = self.getResponse(0)
        maxOffset = response['count']
        offset = 0
        while True:
            if offset >= maxOffset or offset >= 10000 or self.last is not None and self.last in posts:
                break

            self.addPosts(posts, offset)
            offset += 100

        return posts

    def addPosts(self, listIdPosts, offsetCount):
        for i in self.getResponse(offsetCount)['items']:
            listIdPosts[i['id']] = i['text']

    def __del__(self):
        print('Deleted')
