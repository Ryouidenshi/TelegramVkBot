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


advStopWords = ['мы', 'ее', 'между', 'собой', 'но', 'снова', 'там', 'о', 'однажды', 'во время', 'вне', 'очень', 'иметь',
                'с', 'они', 'свой', 'самой', 'или', 'ему', 'каждому', 'тому', 'самим', 'до', 'ниже', 'мы', 'эти',
                'ваши', 'его', 'до', 'не', 'ни', 'я', 'были', 'ее', 'больше', 'он сам', 'это', 'вниз', 'должен', 'наш',
                'их', 'пока', 'выше', 'оба', 'вверх', 'до', 'наш', 'имел', 'она', 'все', 'нет', 'когда', 'в', 'любое',
                'до', 'им', 'то же самое', 'и', 'был', 'имейте', 'в', 'будет', 'на', 'делает', 'вы', 'тогда', 'тот',
                'потому что', 'что', 'над', 'почему', 'так', 'может', 'сделал', 'не', 'сейчас', 'под', 'он', 'ты',
                'сама', 'имеет', 'просто', 'где', 'тоже', 'только', 'я', 'который', 'те', 'я', 'после', 'несколько',
                'кого', 'бытие', 'если', 'их', 'мое', 'против', 'a', 'by', 'делать', 'это', 'как', 'дальше', 'было',
                'здесь', 'то', 'просто']


def get_sortedComments(comments):
    processedComments = ("".join(comments)).lower()
    processedComments = re.sub('[^a-яА-Я]', ' ', processedComments)
    processedComments = re.sub(r'\s+', ' ', processedComments)
    all_sentences = nltk.sent_tokenize(processedComments)
    all_words = [nltk.word_tokenize(sent) for sent in all_sentences]

    for i in range(len(all_words)):
        all_words[i] = [w for w in all_words[i] if len(w) > 2 and (w not in stopwords.words('russian'))
                        and (w not in stopwords.words('english')) and (w not in advStopWords)]
    return all_words


def get_word2vec(comments):
    words = get_sortedComments(comments)
    word2vec = Word2Vec(words, min_count=2)
    return word2vec


def get_bestWords(word2vec):
    vocab = []
    for i in range(0, len(word2vec.wv.index_to_key)):
        if i > 100:
            break
        vocab.append(word2vec.wv.index_to_key[i])
    return vocab


def get_graph(comments, numberImage):
    word2vec = get_word2vec(comments)
    ws = get_bestWords(word2vec)
    words_top_vec = word2vec.wv[ws]
    tsne = TSNE(n_components=2, random_state=0)
    words_top_tsne = tsne.fit_transform(words_top_vec)
    p = figure(tools="pan,wheel_zoom,reset,save",
               toolbar_location="above",
               title="Word2Vec t-SNE for most common words")

    source = ColumnDataSource(data=dict(x1=words_top_tsne[:, 0],
                                        x2=words_top_tsne[:, 1],
                                        names=list(ws)))

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
        executable_path=r'geckodriver.exe',
        options=options)

    export_png(p, filename='picComments/' + str(numberImage) + '.png', webdriver=driver)
    driver.close()

