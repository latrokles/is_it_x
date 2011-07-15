#!/usr/bin/python
#
# filename: test_crawler.py
#
import os
import sys
import unittest

DIR = '/'.join(os.getcwd().split('/')[:-1])
sys.path.append(DIR)

TEST_URL  = 'http://samuraihippo.com'
TECH_URLS = [
             'http://news.ycombinator.com',
             'http://reddit.com',
             'http://wired.com',
            ]

COOKING_URLS = [
                'http://allrecipes.com',
                'http://www.epicurious.com/',
                'http://www.recipe.com/'
               ]

from crawler import Crawler
class CrawlerTestCase(unittest.TestCase):
    '''
    Testing the functionality of the crawler
    '''
    def setUp(self):
        '''
        Create define a data dir, create crawler.
        '''
        self.crawler = Crawler('data')

    def test_download_content(self):
        '''
        Download content from TEST_URL and check against known
        content for said url.
        '''
        content = self.crawler.download_content(TEST_URL)
        assert 'projects' in content
        assert 'resume' in content

    def test_crawl(self):
        '''
        Download the content from a number of urls and save them
        to data directory
        '''
        self.crawler.crawl(TECH_URLS, 'technology')
        self.crawler.crawl(COOKING_URLS, 'cooking')
        assert 'technology' in os.listdir(self.crawler.data_dir)
        assert 'cooking'    in os.listdir(self.crawler.data_dir)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
