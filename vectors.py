import warnings

import numpy as np

warnings.filterwarnings('ignore')
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from selenium.webdriver.firefox.options import Options
from sklearn.manifold import TSNE
import nltk
import re
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.io import export_png
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


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

    def get_vectorComment(self, comm):
        wordsInComment = self.get_sortedWords(comm)
        wv = Word2Vec(wordsInComment, min_count=1).wv.vectors.mean()
        return wv

    @staticmethod
    def get_names(vectorComments):
        names = []
        for i in range(0, len(vectorComments)):
            names.append(' ')
        return names

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

    def get_topics(self, groupsComments):
        topics = {}
        for i in range(0, len(groupsComments)):
            advList = []
            vectorGroup = 0
            for j in range(0, len(groupsComments[i])):
                commentWithVector = groupsComments[i][j].split()
                vectorGroup += float(commentWithVector[-1])
                advList.append(commentWithVector[:len(commentWithVector)-1])
            vectorGroup /= len(groupsComments[i])
            topics[self.get_topic(vectorGroup)] = advList
        return topics

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
        vectorsComments = {}
        for comm in self.comments:
            try:
                vectorsComments[comm] = self.get_vectorComment(comm)
            except RuntimeError:
                continue
        self.update_progress_bar(10)

        groupsComments = self.get_groupComments(vectorsComments)

        topics = self.get_topics(groupsComments)

        self.get_fileTxt(topics)

        tsne = TSNE(n_components=2, random_state=0)

        words_top_tsne = tsne.fit_transform(np.asarray(list(vectorsComments.values())).reshape(-1, 1))
        p = figure(tools="pan,wheel_zoom,reset,save",
                   toolbar_location="above",
                   title="Темы обусждений подписчиков")

        self.update_progress_bar(50)
        source = ColumnDataSource(data=dict(x1=words_top_tsne[:, 0],
                                            x2=words_top_tsne[:, 1],
                                            names=self.get_names(vectorsComments)))

        p.scatter(x="x1", y="x2", size=8, source=source)

        labels = LabelSet(x="x1", y="x2", text="names", y_offset=6,
                          text_font_size="8pt", text_color="#555555",
                          source=source, text_align='center')
        p.add_layout(labels)

        options = Options()
        options.binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", "/Data")
        options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                               "application/octet-stream,application/vnd.ms-excel")
        driver = webdriver.Firefox(
            executable_path=r'data/geckodriver.exe',
            options=options,
            log_path='data/geckodriver.log')

        self.update_progress_bar(75)
        export_png(p, filename='picComments/' + str(self.advNumber) + '.png', webdriver=driver)
        self.update_progress_bar(95)
        driver.close()

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
