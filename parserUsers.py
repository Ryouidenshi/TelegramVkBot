import threading

import requests

errorInputGroup = open('ErrorInputGroup.txt').read()

token = '74414b0d74414b0d74414b0d51743900907744174414b0d148cb840b3a4c7c908271c3d'


def get_offset(offsetCount, groupId):
    count = requests.get('https://api.vk.com/method/groups.getMembers',
                         params={
                             'access_token': token,
                             'v': '5.131',
                             'group_id': groupId,
                             'sort': 'id_desc',
                             'offset': offsetCount,
                             'fields': 'last_seen'
                         })
    if offsetCount == '0':
        return count.json()['response']['count']
    return count.json()['response']


def get_resp(groupId):
    offset = 0
    listResp = []
    maxOffset = get_offset('0', groupId)
    threads = list()
    while offset < maxOffset:
        for i in range(40):
            if offset >= maxOffset:
                break
            x = threading.Thread(target=get_threadResp, args=(listResp, offset, groupId))
            offset += 1000
            threads.append(x)
            x.start()
    [thread.join() for thread in threads]
    return listResp


def get_threadResp(listResp, offset, groupId):
    listResp.append(get_offset(offset, groupId))


def get_usersInGroup(groupId):
    try:
        resp = get_resp(groupId)
        array = []
        for rs in resp:
            for item in rs['items']:
                array.append(item['id'])
        return array
    except Exception:
        return errorInputGroup
