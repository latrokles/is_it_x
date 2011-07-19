#!/usr/bin/python
#
#
import os
import sys
import unittest

DIR = '/'.join(os.getcwd().split('/')[:-1])
sys.path.append(DIR)
from page_classifier import Classifier,simple_get_words, get_words

train_sports = [
    'SPORTS OF THE TIMES; When Americans Are Involved, Fate Can be Fluid',
    'VIDEO GAME REVIEW; EA Sports NCAA Football 12 Goes the Extra Yard',
    'OP-ED COLUMNIST; In Defense of Murdoch',
    'LETTER; Derek Jeter, the Natural',
    ]
train_tech   = [
    'Murdoch Tabloids Targets Included Downing Street and the Crown',
    '7 in Florida Family Are Killed in Plane Crash in Alabama',
    'Scientists Turn to the Web to Raise Research Funds',
    'In Robotics, Human-Style Perception and Motion Are Elusive',
    ]

try:
    from config import DB
except ImportError:
    from my_config import DB

class ClassifierTestCase(unittest.TestCase):
    '''
    Testing the classifier with data for two categories:
        - sports headlines
        - technology headlines

    There is a list of 59 elements in each category, which will be split 50/9
    using 50 elements to train the classifier on each category and the other 9
    to test the trained classifier.
    '''

    def setUp(self):
        '''
        Create the classifier
        '''
        self.classifier = Classifier(get_words, DB)

    def print_features(self):
        '''
        Helper function to see how our feature dictionary changes as it is
        trained.
        '''
        for feat, categories in self.classifier.feat_count.items():
            print feat,'-----------\t',categories

    def test_train_from_file(self):
         '''
         Load a file with a list of headlines and run their contents through the
         trainining process.
         '''
         # test training for a single category at first
         # train with 4 sports headlines
         self.classifier.train_from_file('data/small_train_sports', 'sports')
         #self.print_features()
         # make sure sports is in the list of categories
         assert 'sports' in self.classifier.categories()
         self.classifier.reset_classifier()

         # train with 4 technology headlines
         self.classifier.train_from_file('data/small_train_tech', 'technology')
         #self.print_features()
         # make sure technology is in the list of categories
         assert 'technology' in self.classifier.categories()
         self.classifier.reset_classifier()

         # test training for 2 categories
         self.classifier.train_from_file('data/small_train_sports', 'sports')
         self.classifier.train_from_file('data/small_train_tech', 'technology')
         assert 'sports' in self.classifier.categories()
         assert 'technology' in self.classifier.categories()
         #self.print_features()

    def test_feature_count(self):
         '''
         Test feature count by training classifier with a small listing of sport
         headlines, then look for a few features with known counts and see what
         their count is in the feature dictionary. Do it also for a single training
         item.
         '''
         sports_item = 'SPORTS OF THE TIMES; When Americans Are Involved, Fate Can be Fluid'
         tech_item   = 'Scientists Turn to the Web to Raise Research Funds'
         items_and_category = [
                               (sports_item, 'sports'),
                               (tech_item, 'technology')
                              ]
         for item, category in items_and_category:
             self.classifier.train(item, category)
             item_words = get_words(item).keys()
             for word in item_words:
                 assert self.classifier.feature_count(word, category) == float(item_words.count(word))

    def test_category_count(self):
         '''
         Train from small training files and check the count is equal to
         the size of the file
         '''
         #self.classifier.train_from_file('small_train_sports', 'sports')
         #self.classifier.train_from_file('data/small_train_tech', 'technology')
         training_data = [(train_sports, 'sports'), (train_tech, 'technology')]
         for data, category in training_data:
             f = lambda x: self.classifier.train(x, category)
             map(f, data)
         assert self.classifier.category_count('sports') == 4
         assert self.classifier.category_count('technology') == 4

    def test_feature_probability(self):
        '''
        '''
        pass

    def test_classify(self):
        '''
        Traing with training sets. Then look at the classification results for
        our data for which we know its category.
        '''
        self.classifier = Classifier(simple_get_words, DB)
        training_data = [(train_sports, 'sports'), (train_tech, 'technology')]
        for data, category in training_data:
            f = lambda x: self.classifier.train(x, category)
            map(f, data)
        #self.test_train_from_file()

        sport_item = 'PERSONAL HEALTH; Lurking Menaces Can Threaten the Pleasures of Swimming'
        tech_item  = 'ON THE ROAD; Many Motorists Enraged by Camera-Issued Tickets'

        category_for_sport_item = self.classifier.classify(sport_item)
        #category_for_tech_item  = self.classifier.classify(tech_item)

        print sport_item,':',category_for_sport_item
        #print tech_item,':',category_for_tech_item

        assert category_for_sport_item == 'sports', category_for_sport_item
        #assert category_for_tech_item  == 'technology', category_for_tech_item

    def test_classify_large(self):
        '''
        Test classification with a larger data set, split 50/9 for training/test
        '''
        # training step
        train_tech  = 'data/train_tech'
        train_sport = 'data/train_sports'
        self.classifier.train_from_file(train_tech, 'technology')
        self.classifier.train_from_file(train_sport, 'sports')

        test_tech  = 'data/test_tech'
        test_sport = 'data/test_sports'
        test_data_tech  = open(test_tech, 'r').readlines()
        test_data_sport = open(test_sport, 'r').readlines()

        results_tech  = map(self.classifier.classify, test_data_tech)
        results_sport = map(self.classifier.classify, test_data_sport)

        print results_tech
        print results_sport

    def tearDown(self):
        '''
        '''
        self.classifier.reset_classifier()

if __name__ == '__main__':
    unittest.main()
