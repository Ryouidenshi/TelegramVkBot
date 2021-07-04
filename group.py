class Group:
    doneGroups = []
    groupsIntersection = []
    groups_count = {}

    def __init__(self, idGroups, numberGroupUsers):
        self.idGroups = idGroups
        self.numberGroupUsers = numberGroupUsers
        self.get_doneGroups()
        self.get_groupsIntersection(self.doneGroups)
        self.get_count()

    def get_doneGroups(self):
        existedGroups = {}
        allKeysGroups = self.idGroups.keys()
        for currentGroup in allKeysGroups:
            for advGroup in allKeysGroups:
                if str(advGroup + " и группа " + currentGroup) not in existedGroups \
                        and str(currentGroup + " и группа " + advGroup) \
                        not in existedGroups and currentGroup != advGroup:
                    self.doneGroups.append(self.get_intermediateResult(currentGroup, advGroup,
                                                                       self.idGroups[currentGroup],
                                                                       self.idGroups[advGroup], existedGroups))
        self.get_fileTxt(self.doneGroups)

    def get_fileTxt(self, listIntersection):
        fileTxt = open('data/dataUsers' + str(self.numberGroupUsers) + '.txt', 'w')
        for item in listIntersection:
            keys = item.keys()
            for key in keys:
                fileTxt.write(key + " " + str(item[key]) + "\n")

    def get_count(self):
        keys = self.idGroups.keys()
        for keyForCount in keys:
            self.groups_count[keyForCount] = len(self.idGroups[keyForCount])

    @staticmethod
    def get_groupsIntersection(doneGroups):
        for gr in doneGroups:
            if gr is not None:
                keys = gr.keys()
                for key in keys:
                    if gr[key] != 0:
                        userGroups_split = str(gr[key]).split()
                        list_split = str(key).split()
                        Group.groupsIntersection.append([list_split[0], list_split[3], len(userGroups_split)])

    @staticmethod
    def get_intermediateResult(currentGroup, advGroup, groupCurrent, groupSecond, existedGroups):
        intermediateResult = {}
        intersection = set(groupCurrent).intersection(set(groupSecond))
        intermediateResult[currentGroup + " и группа " + advGroup] = intersection
        existedGroups[currentGroup + " и группа " + advGroup] = 0
        return intermediateResult

    def __del__(self):
        print('Deleted')
