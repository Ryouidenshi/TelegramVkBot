import threading

import requests

import parserPosts

errorInputGroup = open('helpingFiles/ErrorInputGroupForFindUsers.txt').read()

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


def get_allComments(groupDomain, listComments=None):
    if listComments is None:
        listComments = []
    try:
        postsId = split_postsId(parserPosts.get_idPosts(groupDomain))
    except Exception:
        errorFoundGroup = open('helpingFiles/ErrorFoundGroup.txt')
        return errorFoundGroup
    idGroup = parserPosts.get_response(0, groupDomain)['items'][0]['owner_id']
    timeNewestComment = get_response(0, idGroup, postsId[0])['items'][0]['date']

    countParsedComments = 0
    threads = list()
    for post in range(0, len(postsId)):
        if countParsedComments >= 100000:
            break
        x = threading.Thread(target=add_comment, args=(listComments, 0, idGroup, postsId[post]))
        threads.append(x)
        x.start()
        countParsedComments += 100
    [thread.join() for thread in threads]
    fileTime = open('data/PreviousDate.txt', 'a')
    fileTime.write(groupDomain + " " + str(timeNewestComment) + "\n")
    return listComments


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
