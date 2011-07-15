#!/usr/bin/python
#
# filename: page_classifier.py
#
#
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer
from nltk import WordNetLemmatizer, FreqDist
STOPWORDS = stopwords.words('english')
import codecs, re
def get_words(document):
    '''
    Return a list of unique words in document
    '''
    regex1 = re.compile('\(^[A-Za-z]\)*')          # match non-alphanumeric
    regex2 = re.compile('&(#)*(\w)*;')  # match html entities
    regex3 = re.compile('( ){2,}')      # match more than 2 spaces
    lemmatizer = WordNetLemmatizer()
    tokenizer  = WhitespaceTokenizer()
    # lowercase document, remove punctuation, and html entities
    document   = regex3.sub(' ', regex2.sub(' ', regex1.sub(' ', document.lower())))
    words = [
             lemmatizer.lemmatize(word)
             for word in tokenizer.tokenize(document)
             if word not in STOPWORDS and len(word) > 2
            ]
    return FreqDist(words)

def simple_get_words(document):
    splitter = re.compile('\\W*')
    words = [s.lower() for s in splitter.split(document) if len(s) > 2 and len(s)<20]
    return dict([(w,1) for w in words])

class Classifier(object):
    '''
    An implementation of a naive Bayes classifier based on the material from
    chapter 6 of O'Reilly's "Programming Collective Intelligence"
    '''
    def __init__(self, get_features):
        # keep track of the count for a given feature in each category
        self.feat_count = { }
        # keep track of the document count in each  category
        self.cat_count  = { }
        # we set our function to extract features, we can use the same
        # classifier
        # for different kinds of features
        self.get_features = get_features
        # thresholds for making a final classification decision
        self.thresholds = { }

    def increment_feature(self, feat, cat):
        '''
        Increment the count of feat in cat. If cat doesn't exist for feature,
        add it and increment.
        '''
        self.feat_count.setdefault(feat, {})
        self.feat_count[feat].setdefault(cat, 0)
        self.feat_count[feat][cat] += 1

    def increment_category(self, cat):
        '''
        Increment the count of a category
        '''
        self.cat_count.setdefault(cat, 0)
        self.cat_count[cat] += 1

    def feature_count(self, feat, cat):
        '''
        Returns the number of counts feat is in cat
        '''
        if feat in self.feat_count and cat in self.feat_count[feat]:
            return float(self.feat_count[feat][cat])
        return 0.0  # else return 0

    def category_count(self, cat):
        '''
        Return the count of documents in cat
        '''
        if cat in self.cat_count:
            return float(self.cat_count[cat])
        return 0.0

    def total_count(self):
        '''
        Returns the total number of documents.
        '''
        return sum(self.cat_count.values())

    def categories(self):
        '''
        Returns a list of all categories
        '''
        return self.cat_count.keys()

    def train(self, item, cat):
        '''
        Takes an item classified under cat, extracts its features, and
        increments the count of that feature inside that cat.
        '''
        item_features = self.get_features(item)
        # increment the count for each feature in cat
        for feature in item_features:
            self.increment_feature(feature, cat)
        # increment the count for cat
        self.increment_category(cat)

    def train_from_file(self, filename, cat):
        '''
        Retrieve documents in training file (as single line entries) and train
        the classifier with them.
        '''
        lines = [ ]
        with codecs.open(filename, 'r', 'utf-8') as file:
            lines = file.readlines()
        for item in lines:
            self.train(item.strip('\n'), cat)

    def reset_classifier(self):
        '''
        Clears out feat_count and cat_count dictionaries. Very helpful for
        testing and for use in the python shell
        '''
        self.feat_count = { }
        self.cat_count  = { }
        self.thresholds = { }

    # calculate probabilities
    def feature_probability(self, feat, cat):
        '''
        Calculate the probability that a feature is in a given category.
        '''
        if self.category_count(cat) == 0:
            return 0
        # total count of feat in cat / total count of items in cat
        feature_p = self.feature_count(feat, cat) / self.category_count(cat)
        return feature_p

    def weighted_probability(self, feat, cat, weight=1.0, assumed_p=0.5):
        '''
        We take the weighted probability for feat in cat in order to avoid
        bias to early training data.
        '''
        basic_p = self.feature_probability(feat, cat)

        # get a total count for this feature in all categories
        total_count = sum(
                          [
                           self.feature_count(feat, c)
                           for c in self.categories()
                          ]
                         )
        # calculate the weighted average
        weighted_prob = ((weight * assumed_p) + (total_count*basic_p)) / (weight+total_count)
        return weighted_prob

    def document_probability(self, document, cat):
        '''
        '''
        # get the geatures for the document
        features = self.get_features(document)
        p = 1
        # multiply the probabilities of all the features together
        for feature in features:
            p *= self.weighted_probability(feature, cat)
        return p

    def probability(self, document, cat):
        '''
        Calculates the probability document is in cat
        '''
        category_probability = self.category_count(cat) / self.total_count()
        document_probability = self.document_probability(document, cat)
        return document_probability * category_probability

    # classification functions
    def set_threshold(self, cat, threshold):
        '''
        Set a threshold for cat to determine minimum differences in their
        probabilities in order to be classifed under a given category
        '''
        self.thresholds[cat] = threshold

    def get_threshold(self, cat):
        '''
        Returns the threshold for cat
        '''
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]

    def classify(self, document):
        '''
        Find what category document falls into
        '''
        probabilities = { }
        max = 0.0
        # get category with highest probability for document
        for category in self.categories():
            probabilities[category] = self.probability(document, category)
            if probabilities[category] > max:
                max = probabilities[category]
                best = category
        # check that probability exceeds the threshold * next best category
        for category, probability in probabilities.items():
            if category == best:
                continue
            if probability * self.get_threshold(best) > probabilities[best]:
                return None
        return best
