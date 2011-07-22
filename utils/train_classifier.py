#!/usr/bin/python
#
# Quick script to train classifier with data from a file.
#
#
import sys, os
DIR = '/'.join(os.getcwd().split('/')[:-1])
sys.path.append(DIR)
import page_classifier

# read data for file and label (assuming file is in data dir)
file_path, label = sys.argv[1], sys.argv[2]
# read the data for the database from command line
# dbname, host, usr, passwd
DB = {}
DB['dbname'], DB['host'], DB['usr'], DB['passwd'] = sys.argv[3:]

# create our classifier
classifier = page_classifier.Classifier(page_classifier.get_words, DB)

# train it from file
classifier.train_from_file(file_path, label)
