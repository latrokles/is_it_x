#!/usr/bin/python
#
# filename: page_classifier.py
#
#
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer
from nltk import WordNetLemmatizer, FreqDist
STOPWORDS = stopwords.words('english')
import codecs, re, math
import MySQLdb as mysql

def get_words(document):
    '''
    Return a list of unique words in document
    '''
    regex1 = re.compile('\W')          # match non-alphanumeric
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
    def __init__(self, get_features, db):
        '''
        Initializes the classifier with an empty feature count, category count,
        thresholds, and a connection to the database.

        The arguments:
            - get_features: a function that takes a string or document and
                            returns a list of features.
            - db: a dictionary with the information to connect to the database
                  where the classifier stores the trained model. This dict has
                  the following keys: dbname, host, usr, passwd.
        '''
        # set our connection to the database
        self.db = mysql.connect(
                                host=db['host'],
                                user=db['usr'],
                                passwd=db['passwd'],
                                db=db['dbname']
                               )
        self.cursor = self.db.cursor()
        # we set our function to extract features, we can use the same
        # classifier for different kinds of features
        self.get_features = get_features
        # thresholds for making a final classification decision
        self.thresholds = { }

    def increment_feature(self, feat, cat):
        '''
        Increment the count of feat in cat. If cat doesn't exist for feature,
        add it and increment.
        '''
        # get the count
        count = self.feature_count(feat, cat)
        if count == 0:
            # create record for this feature on this category
            self.cursor.execute(
                                '''
                                INSERT INTO feature_tbl
                                (feature, category, count) VALUES (%s, %s, %s)
                                ''',
                                (feat, cat, 1)
                               )
        else:
            # update the count for feature in category
            self.cursor.execute(
                                '''
                                UPDATE feature_tbl SET count=%s
                                WHERE feature=%s AND category=%s
                                ''',
                                (count+1, feat, cat)
                               )
        self.db.commit()

    def increment_category(self, cat):
        '''
        Increment the count of a category
        '''
        # get the category count
        count = self.category_count(cat)
        if count == 0:
            # create new record for category
            self.cursor.execute(
                                '''
                                INSERT INTO category_tbl (category, count)
                                VALUES (%s, %s)
                                ''',
                                (cat, 1)
                               )
        else:
            # increment the count of the category
            self.cursor.execute(
                                '''
                                UPDATE category_tbl SET count=%s
                                WHERE category=%s
                                ''',
                                (count+1, cat)
                               )
        self.db.commit()

    def feature_count(self, feat, cat):
        '''
        Returns the number of counts feat is in cat
        '''
        self.cursor.execute(
                            '''
                            SELECT count FROM feature_tbl
                            WHERE feature=%s AND category=%s
                            ''',
                            (feat, cat)
                           )
        result = self.cursor.fetchone()
        if result == None:
            return 0.0
        else:
            return float(result[0])

    def category_count(self, cat):
        '''
        Return the count of documents in cat
        '''
        self.cursor.execute(
                       '''
                       SELECT count FROM category_tbl
                       WHERE category=%s
                       ''',
                       (cat,)
                      )
        result = self.cursor.fetchone()
        if result == None:
            return 0.0
        else:
            return float(result[0])

    def total_count(self):
        '''
        Returns the total number of documents.
        '''
        self.cursor.execute('''SELECT SUM(count) FROM category_tbl''')
        total_document_count = int(self.cursor.fetchone()[0])
        return total_document_count

    def categories(self):
        '''
        Returns a list of all categories
        '''
        self.cursor.execute('''SELECT category FROM category_tbl''')
        categories = [ category for category, in self.cursor.fetchall() ]
        return categories

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
        with open(filename, 'r') as file:
            lines = file.readlines()
            for item in lines:
                self.train(item, cat)

    def reset_classifier(self):
        '''
        Clears out the feature and category tables as well as the thresholds
        dictionary. Very helpful for testing and for use in the python shell
        '''
        # clear the feature and category tables in the DB
        self.cursor.execute('''DELETE FROM feature_tbl''')
        self.cursor.execute('''DELETE FROM category_tbl''')
        self.db.commit()
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
            wp = self.weighted_probability(feature, cat)
            #p *= wp
            p += math.log(wp)
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
        #max = 0.0
        # get category with highest probability for document
        for category in self.categories():
            probabilities[category] = self.probability(document, category)
            #print 'Probablity document is in %s: %f' % (category, probabilities[category])
            #if probabilities[category] > max:
            #    max = probabilities[category]
            #    best = category
        best = max(probabilities, key=probabilities.get)
        # check that probability exceeds the threshold * next best category
        #for category, probability in probabilities.items():
        #    if category == best:
        #        continue
        #    if probability * self.get_threshold(best) > probabilities[best]:
        #        return None
        return best
