#!/usr/bin/python
#
#
# This is a quick script to download training data, can do with lots of
# improvement though.
#

import sys, os
DIR = '/'.join(os.getcwd().split('/')[:-1])
sys.path.append(DIR)
import crawler

# get the path to the file with a url or list of urls and the label for the
# data at said url from the command line
url_file, label = sys.argv[1], sys.argv[2]

# create our crawler
downloader = crawler.Crawler(DIR + os.sep + 'data', True)

# get list of urls
with open(url_file, 'r') as link_file:
    urls = map(lambda x: x.strip('\n'), link_file.readlines())

# download our content
downloader.crawl(urls, label)
