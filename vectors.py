import threading
import warnings

import numpy as np
from sklearn.cluster import KMeans

warnings.filterwarnings('ignore')
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from sklearn.manifold import TSNE
import nltk
import re
import matplotlib.pyplot as plt


class Vectors:
    def __init__(self, comments, advNumber, progressMessage, bot):
        self.comments = comments
        self.advNumber = advNumber
        self.progressMessage = progressMessage
        self.bot = bot

    advStopWords = ['мы', 'ее', 'между', 'собой', 'но', 'снова', 'там', 'о', 'однажды', 'во время', 'вне', 'очень',
                    'иметь',
                    'с', 'они', 'свой', 'самой', 'или', 'ему', 'каждому', 'тому', 'самим', 'до', 'ниже', 'мы', 'эти',
                    'ваши', 'его', 'до', 'не', 'ни', 'я', 'были', 'ее', 'больше', 'он сам', 'это', 'вниз', 'должен',
                    'наш',
                    'их', 'пока', 'выше', 'оба', 'вверх', 'до', 'наш', 'имел', 'она', 'все', 'нет', 'когда', 'в',
                    'любое',
                    'до', 'им', 'то же самое', 'и', 'был', 'имейте', 'в', 'будет', 'на', 'делает', 'вы', 'тогда', 'тот',
                    'потому что', 'что', 'над', 'почему', 'так', 'может', 'сделал', 'не', 'сейчас', 'под', 'он', 'ты',
                    'сама', 'имеет', 'просто', 'где', 'тоже', 'только', 'я', 'который', 'те', 'я', 'после', 'несколько',
                    'кого', 'бытие', 'если', 'их', 'мое', 'против', 'a', 'by', 'делать', 'это', 'как', 'дальше', 'было',
                    'здесь', 'то', 'просто']

    def get_sortedWords(self, comment):
        processedComments = ("".join(comment)).lower()
        processedComments = re.sub('[^a-яА-Я]', ' ', processedComments)
        processedComments = re.sub(r'\s+', ' ', processedComments)
        all_sentences = nltk.sent_tokenize(processedComments)
        wordsInComment = [nltk.word_tokenize(sent) for sent in all_sentences]

        for i in range(len(wordsInComment)):
            wordsInComment[i] = [w for w in wordsInComment[i] if len(w) > 2 and (w not in stopwords.words('russian'))
                                 and (w not in stopwords.words('english')) and (w not in self.advStopWords)]
        return wordsInComment

    def get_vectorsComments(self):
        vectorComments = {}
        threads = list()
        count = 0
        listComments = []
        vectors = []
        for comment in self.comments:
            if count <= 40:
                try:
                    count += 1
                    wordsInComment = self.get_sortedWords(comment)
                    vector = Word2Vec(wordsInComment, min_count=1).wv.vectors.mean()
                    listComments.append(comment)
                    vectors.append(vector)
                except RuntimeError:
                    continue
            else:
                x = threading.Thread(target=self.get_vectorComment, args=(vectorComments,
                                                                          listComments,
                                                                          vectors))
                threads.append(x)
                count = 0
                listComments = []
                vectors = []
                x.start()
        [thread.join() for thread in threads]
        threads.clear()
        return vectorComments

    def get_vectorComment(self, vectorComments, comments, vectors):
        for i in range(0, len(comments)):
            #wordsInComment = self.get_sortedWords(comment)
            #wv = Word2Vec(wordsInComment, min_count=1).wv.vectors.mean()
            vectorComments[comments[i]] = vectors[i]

    @staticmethod
    def get_groupComments(vectorComments):
        group = []
        keys = vectorComments.keys()
        for currentComm in keys:
            if currentComm + ' ' + str(vectorComments[currentComm]) in [element for a_list in group for element in
                                                                        a_list]:
                continue
            advList = []
            for othComm in keys:
                if othComm + ' ' + str(vectorComments[othComm]) in advList:
                    continue
                if abs(vectorComments[currentComm] - vectorComments[othComm]) < 0.0001:
                    advList.append(othComm + ' ' + str(vectorComments[othComm]))
            group.append(advList)
        return group

    def get_topic(self, vector):
        topic = ' '
        differenceValueVector = 1000.0
        words = self.get_sortedWords(self.comments)
        word2vec = Word2Vec(words, min_count=1)
        for i in words:
            for j in i:
                if abs(word2vec.wv[j].mean() - vector) < differenceValueVector:
                    differenceValueVector = abs(word2vec.wv[j].mean() - vector)
                    topic = j
        return topic

    def get_graph(self):
        vectorsComments = self.get_vectorsComments()
        #self.get_fileTxt(topics)

        tsne = TSNE(n_components=2, random_state=0)
        words_top_tsne = tsne.fit_transform(np.asarray(list(vectorsComments.values())).reshape(-1, 1))
        x_axis = words_top_tsne[:, 0]
        y_axis = words_top_tsne[:, 1]
        inertia = []
        countClusters = 0
        for k in range(1, 8):
            kMeans = KMeans(n_clusters=k, random_state=1).fit(words_top_tsne)
            inertia.append(np.sqrt(kMeans.inertia_))
        for i in range(0, len(inertia)):
            if abs(inertia[i] - inertia[i + 1]) < 1:
                break
            countClusters += 1

        kMeans = KMeans(n_clusters=countClusters)
        kMeans.fit(words_top_tsne)

        plt.scatter(x_axis, y_axis, s=8, c=kMeans.labels_)
        plt.savefig('picComments/' + str(self.advNumber) + '.png')

        self.update_progress_bar(50)

    def get_fileTxt(self, topics):
        fileTxt = open('data/dataComments' + str(self.advNumber) + '.txt', 'w')
        fileTxt.write('-----------------------------------\n')
        keys = topics.keys()
        counter = 1
        for topic in keys:
            # noinspection PyBroadException
            try:
                fileTxt.write(str(counter) + ' - ' + topic + "\n")
                countComments = 0
                fileTxt.write('Комментарий: ')
                for i in topics[topic]:
                    if countComments > 10:
                        break
                    isEmpty = 0
                    for j in i:
                        # noinspection PyBroadException
                        try:
                            fileTxt.write(j + " ")
                            isEmpty += 1
                        except Exception:
                            continue
                    if isEmpty != 0:
                        fileTxt.write("\n")
                    countComments += 1
                counter += 1
                fileTxt.write('-----------------------------------\n')
            except Exception:
                continue

    # Немного костыльная дичь с проносом ProgressMessage и bot через некоторые методы парсинга,
    # если у кого есть идеи как реализовать прогресс бар лучше и с меньшим количеством костылей - напишите в конфе
    def update_progress_bar(self, percent):
        countBar = (percent // 10)
        strBarPercent = '[' + '|' * int(countBar) + ' ' * ((10 - int(countBar)) * 2) + '] - ' + str(percent) + '%'
        self.bot.edit_message_text('Подождите, проводим анализ:\n' + strBarPercent,
                                   self.progressMessage.chat.id, self.progressMessage.message_id)

    def __del__(self):
        print('Deleted')

