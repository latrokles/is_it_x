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
'''
from flask import Flask

app = Flask(__name__)


if __name__ == '__main__':
    app.run()
