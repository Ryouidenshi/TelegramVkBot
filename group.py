def get_doneGroups(groups, txtNumber):
    doneGroups = []
    existedGroups = {}
    allKeysGroups = groups.keys()
    for currentGroup in allKeysGroups:
        for advGroup in allKeysGroups:
            if str(advGroup + " и группа " + currentGroup) not in existedGroups \
                    and str(currentGroup + " и группа " + advGroup) not in existedGroups and currentGroup != advGroup:
                doneGroups.append(get_intermediateResult(currentGroup, advGroup,
                                                         groups[currentGroup], groups[advGroup], existedGroups))
    get_fileTxt(doneGroups, txtNumber)
    return doneGroups


def get_intermediateResult(currentGroup, advGroup, groupCurrent, groupSecond, existedGroups):
    intermediateResult = {}
    intersection = set(groupCurrent).intersection(set(groupSecond))
    intermediateResult[currentGroup + " и группа " + advGroup] = intersection
    existedGroups[currentGroup + " и группа " + advGroup] = 0
    return intermediateResult


def get_fileTxt(listIntersection, txtNumber):
    fileTxt = open('data/dataUsers' + str(txtNumber) + '.txt', 'w')
    for item in listIntersection:
        keys = item.keys()
        for key in keys:
            fileTxt.write(key + " " + str(item[key]) + "\n")



def get_count(group):
    return len(group)
