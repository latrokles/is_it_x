#!/usr/bin/python
#
# filename: is_it_x.py
#
#
'''
Web frontend to is_it_x app.

URL structure:
 /                --> main page with form for url
 /classify/       --> retrieves data from url, classifies it and shows result
 /report_mistake/ --> reports a mistaken classification, trains app with page
 /error/          --> prints out error when given an invalid URL
'''
from flask import Flask, request, render_template, redirect, url_for
from config import *
import crawler, page_classifier
app = Flask(__name__)

@app.route('/')
def main_page():
    '''
    Displays the form for the user to type or paste the url for the page to
    check.
    '''
    return render_template('index.html')

@app.route('/classify/', methods=['POST'])
def classify():
    '''
    Processes the form with the url to check, downloads the content at that
    url and classifies it. It then returns whether the content at the url falls
    in category X
    '''
    if request.method == 'POST':
        # create our crawler and classifier
        page_crawler = crawler.Crawler()
        classifier   = page_classifier.Classifier(page_classifier.get_words,DB)
        url = request.form['domain']
        if url[:7] != 'http://':
            url = 'http://' + url
        url_error = ''
        # get the page's content
        try:
            url_content = page_crawler.download_content(url)
        except crawler.CrawlerError:
            return redirect(url_for('error'))
        # get the classification for the text
        # determine if text is classified as X and return as such
        classification = classifier.classify(url_content)
        if classification == X:
            result = 'Yes %s is %s' % (url, X)
        else:
            result = 'No %s is NOT %s' % (url, X)

        return render_template('result.html', message=result, url=url)
    else:
        return redirect(url_for('main_page'))

@app.route('/error/')
def error():
    '''
    Displays an error page.
    '''
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
