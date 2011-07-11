#!/usr/bin/python
#
# filename: crawler.py
#
'''
This script goes to specific websites and downloads some pages in order to
build a decently sized training data set.
'''
import urllib2, os, codecs, re
from BeautifulSoup import BeautifulSoup

class Crawler(object):
    '''
    The crawler goes to a page and downloads the text content along with any
    urls in it, labels it, and appends all this to the training data set for
    that label
    '''
    def __init__(self, data_dir=None):
        '''
        data_dir: location to store the data downloaded
        '''
        self.data_dir = data_dir
        if data_dir is None:
            self.download = False
        else:
            self.download = True

    def crawl(self, pages, label):
        '''
        pages: a list of pages to crawl
        label: label to give to the content downloaded, also name of the file
               to which the content gets downloaded
        '''
        documents = [ ]
        for page in pages:
            content = self.download_content(page)
            documents.append(content)
        if self.download:
            documents_to_write = '\n'.join(documents)
            with codecs.open(self.data_dir + os.sep + label, 'a', 'utf-8') as file:
                file.write(documents_to_write)

    def download_content(self, page_url):
        '''
        Opens the page, downloads the content, and returns it as a string.
        '''
        regex = re.compile('\n')
        data = urllib2.urlopen(page_url).read()
        soup = BeautifulSoup(data)
        content = regex.sub(' ', self.parse_content(soup))
        return content + '\n'

    def parse_content(self, soup):
        '''
        Takes the html of the page and extracts the text from it along with any
        urls found in the page.
        '''
        value = soup.string
        if value == None:
            content = soup.contents
            result_text = u''
            for tag in content:
                try:
                    if tag.name == 'style' or tag.name == 'script':
                        # we dont' care about this data, yet
                        continue
                except AttributeError:
                    # if tag has no name attribute, we don't really care
                    # still, get its contents
                    print 'ERROR: %s has no name' % (tag,)
                subtext = self.parse_content(tag)
                result_text += u' ' + subtext
            return result_text
        else:
            return value.strip( )

if __name__ == '__main__':
    crawler = Crawler('data')
    urls_to_crawl = [
                     'http://reddit.com',
                     'http://wired.com',
                     'http://news.ycombinator.com'
                    ]
    crawler.crawl(urls_to_crawl, 'tech_news')

