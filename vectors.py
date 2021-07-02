import re
import nltk
from nltk.corpus import stopwords
from gensim.models import Word2Vec
import warnings
warnings.filterwarnings('ignore')

advStopWords = ['она', 'они', 'оно', 'you', 'это', 'эта', 'эти']


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


def get_vectors(comments):
    words = get_sortedComments(comments)
    word2vec = Word2Vec(words, min_count=2)
    vocab = word2vec.wv.index_to_key
    f = 0

