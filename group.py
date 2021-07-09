class Groups:

    def __init__(self, idGroups, requestNumberGroup):
        self.idGroups = idGroups
        self.requestNumberGroup = requestNumberGroup
        self.viewedGroups = self.getViewedGroups()
        self.groupsDifference = self.getGroupsDifference()
        self.groupsIntersection = self.getGroupsIntersection()
        self.getCountsUsersInGroups = self.getCountsUsersInGroups()

    def getGroupsDifference(self):
        groupsDifference = []
        existedGroups = {}
        allKeysGroups = self.idGroups.keys()
        mainGroup = list(allKeysGroups)[0]
        for currentGroup in allKeysGroups:
            if currentGroup == mainGroup:
                continue
            groupsDifference.append(self.get_differenceResult(mainGroup, currentGroup,
                                                              self.idGroups[mainGroup],
                                                              self.idGroups[currentGroup], existedGroups))
        return groupsDifference

    def getViewedGroups(self):
        viewedGroups = []
        existedGroups = {}
        allKeysGroups = self.idGroups.keys()
        for currentGroup in allKeysGroups:
            for otherGroup in allKeysGroups:
                if str(otherGroup + " и группа " + currentGroup) not in existedGroups \
                        and str(currentGroup + " и группа " + otherGroup) \
                        not in existedGroups and currentGroup != otherGroup:
                    viewedGroups.append(self.getIntermediateResult(currentGroup, otherGroup,
                                                                   self.idGroups[currentGroup],
                                                                   self.idGroups[otherGroup], existedGroups))
        return viewedGroups

    def getFileTxt(self):
        fileTxt = open('dataUsers/' + str(self.requestNumberGroup) + '.txt', 'w')
        for difference in self.groupsDifference:
            keys = difference.keys()
            for key in keys:
                fileTxt.write(key + " " + str(difference[key]) + "\n")

    def getCountsUsersInGroups(self):
        groupsCount = {}
        keys = self.idGroups.keys()
        for keyForCount in keys:
            groupsCount[keyForCount] = len(self.idGroups[keyForCount])
        return groupsCount

    def getGroupsIntersection(self):
        groupsIntersection = []
        for gr in self.viewedGroups:
            if gr is not None:
                keys = gr.keys()
                for key in keys:
                    if gr[key] != 0:
                        userGroups_split = str(gr[key]).split()
                        list_split = str(key).split()
                        groupsIntersection.append([list_split[0], list_split[3], len(userGroups_split)])
        return groupsIntersection

    @staticmethod
    def getIntermediateResult(currentNameGroup, otherNameGroup, currentGroup, otherGroup, existedGroups):
        intermediateResult = {}
        intersection = set(currentGroup).intersection(set(otherGroup))
        intermediateResult[currentNameGroup + " и группа " + otherNameGroup] = intersection
        existedGroups[currentNameGroup + " и группа " + otherNameGroup] = 0
        return intermediateResult

    @staticmethod
    def get_differenceResult(currentGroup, advGroup, groupCurrent, groupSecond, existedGroups):
        differenceResult = {}
        difference = set(groupSecond).difference(set(groupCurrent))
        if len(difference) > 1000000:
            difference = set(list(difference)[:1000000])
        differenceResult["Список с ID пользователей группы " + advGroup +
                         ", которых нет в вашей группе " + currentGroup + "\n"] = difference
        existedGroups[currentGroup + " и группа " + advGroup] = 0
        return differenceResult

    def __del__(self):
        print('DeletedGroupUsers')
