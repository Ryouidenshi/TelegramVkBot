import threading

import requests

errorInputGroup = open('helpingFiles/ErrorFoundGroup.txt').read()

token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'


def get_response(offsetCount, groupDomain):
    return requests.get('https://api.vk.com/method/wall.get',
                        params={
                            'access_token': token,
                            'v': '5.131',
                            'domain': groupDomain,
                            'count': 100,
                            'sort': 'desc',
                            'offset': offsetCount
                        }).json()['response']


def get_idPosts(groupDomain, listIdPosts=None):
    if listIdPosts is None:
        listIdPosts = []
    response = get_response(0, groupDomain)
    maxOffset = response['count']
    offset = 0
    threads = list()
    while True:
        if offset >= maxOffset or offset >= 1000:
            break
        x = threading.Thread(target=add_posts, args=(listIdPosts, offset, groupDomain))
        offset += 100
        threads.append(x)
        x.start()
    [thread.join() for thread in threads]
    return listIdPosts


def add_posts(listIdPosts, offsetCount, groupDomain):
    for i in get_response(offsetCount, groupDomain)['items']:
        listIdPosts.append(i['id'])