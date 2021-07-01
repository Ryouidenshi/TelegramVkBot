import threading

import requests

errorInputGroup = open('ErrorInputGroup.txt').read()

token = '97e0797797e0797797e07977089798170c997e097e07977f73dfa498a09c0bebff270ba'


def get_postsId(offsetCount, groupId, isIdGroup):
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': token,
                         'v': '5.131',
                         'domain': groupId,
                         'count': 100,
                         'sort': 'desc',
                         'offset': offsetCount
                     })
    if isIdGroup:
        return r.json()['response']['items'][0]['owner_id']
    if offsetCount == '0':
        return r.json()['response']['count']
    r = r.json()['response']['items']
    commentsId = []
    for i in r:
        commentsId.append(i['id'])
    return commentsId


def get_comments(offsetCount, idGroup, postId, isTime):
    r = requests.get('https://api.vk.com/method/wall.getComments',
                     params={
                         'access_token': token,
                         'owner_id': idGroup,
                         'v': '5.131',
                         'post_id': postId,
                         'count': 100,
                         'sort': 'desc',
                         'offset': offsetCount
                     })
    if isTime:
        return r.json()['response']['items'][0]['date']
    if offsetCount == '0':
        return r.json()['response']['count']
    r = r.json()['response']['items']
    comments = []
    for i in r:
        try:
            comments.append(i['text'])
        except Exception:
            break
    return comments


def get_allIdPosts(groupDomain):
    maxOffset = get_postsId('0', groupDomain, False)
    listId = []
    offset = 0
    threads = list()
    while offset < maxOffset and offset <= 1000:
        for i in range(40):
            if offset >= maxOffset or offset > 1000:
                break
            x = threading.Thread(target=get_multithreading, args=(listId, offset, groupDomain))
            offset += 100
            threads.append(x)
            x.start()
    [thread.join() for thread in threads]
    return listId


def get_multithreading(listId, offsetCount, groupId):
    listId.append(get_postsId(offsetCount, groupId, False))


def get_allComments(groupDomain):
    postsId = split_posts(get_allIdPosts(groupDomain))
    idGroup = get_postsId('0', groupDomain, True)
    lastParsingComment = get_comments(0, idGroup, postsId[0], True)
    listComments = []
    countCom = 0
    threads = list()
    for post in range(0, len(postsId)):
        if countCom > 100000:
            break
        x = threading.Thread(target=add_comm, args=(listComments, 0, idGroup, postsId[post]))
        threads.append(x)
        x.start()
        countCom += 100
    [thread.join() for thread in threads]
    fileTime = open('data/PreviousDate.txt', 'a')
    fileTime.write(groupDomain + " " + str(lastParsingComment) + "\n")
    return listComments


def add_comm(listCom, offset, idGroup, postId):
    listCom.append(get_comments(offset, idGroup, postId, False))


def split_posts(postsId):
    res = []
    threads = list()
    for p in postsId:
        x = threading.Thread(target=add_post, args=(res, p))
        threads.append(x)
        x.start()
    [thread.join() for thread in threads]
    return res


def add_post(res, p):
    for j in p:
        res.append(j)
