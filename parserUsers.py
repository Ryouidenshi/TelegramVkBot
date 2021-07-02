import threading

import requests

errorInputGroupForFindUsers = open('helpingFiles/ErrorFoundGroup.txt').read()

token = '74414b0d74414b0d74414b0d51743900907744174414b0d148cb840b3a4c7c908271c3d'


def get_response(offsetCount, groupId):
    return requests.get('https://api.vk.com/method/groups.getMembers',
                        params={
                            'access_token': token,
                            'v': '5.131',
                            'group_id': groupId,
                            'sort': 'id_desc',
                            'offset': offsetCount,
                            'fields': 'last_seen'
                        }).json()['response']


def get_resp(groupId, listResponses=None):
    if listResponses is None:
        listResponses = []
    offset = 0
    maxOffset = get_response(0, groupId)['count']
    threads = list()
    while True:
        if offset > maxOffset:
            break
        x = threading.Thread(target=get_threadResp, args=(listResponses, offset, groupId))
        offset += 1000
        threads.append(x)
        x.start()
    [thread.join() for thread in threads]
    return listResponses


def get_threadResp(listResponses, offset, groupId):
    listResponses.append(get_response(offset, groupId))


def get_usersInGroup(groupId, listUsersInGroup=None):
    if listUsersInGroup is None:
        listUsersInGroup = []
    try:
        responses = get_resp(groupId)
        for response in responses:
            for item in response['items']:
                listUsersInGroup.append(item['id'])
        return listUsersInGroup
    except Exception:
        errorInputGroupForFindUsers = open('helpingFiles/ErrorFoundGroup.txt').read()
        return errorInputGroupForFindUsers
