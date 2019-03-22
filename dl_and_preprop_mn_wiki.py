#!/usr/bin/env python3
"""Download and pre process the Mongolian Wikipedia."""
__author__ = 'Erdene-Ochir Tuguldur'

import os
import glob
from os.path import join, exists
from utils import download_file, sentence_tokenize

MN_WIKI_FILE = 'mn_wiki.txt'
MN_CORPUS_FOLDER = 'mn_corpus'
MN_WIKI_RAR_FILE = 'mn_wiki.bz2'
MN_WIKI_EXTRACT_FOLDER = 'tmp_mn_wiki'
MN_WIKI_URL = 'https://dumps.wikimedia.org/mnwiki/20181220/mnwiki-20181220-pages-articles-multistream.xml.bz2'


# create corpus directory
if not exists(MN_CORPUS_FOLDER):
    os.makedirs(MN_CORPUS_FOLDER)

# download
if not exists(MN_WIKI_RAR_FILE):
    download_file(MN_WIKI_URL, MN_WIKI_RAR_FILE)

# extract
os.system("python3 wikiextractor/WikiExtractor.py %s -o=%s" % (MN_WIKI_RAR_FILE, MN_WIKI_EXTRACT_FOLDER))


def _pre_process(wiki_file_name):
    """a very simple pre processing"""
    print("pre processing '%s'..." % wiki_file_name)
    with open(wiki_file_name) as f:
        content = f.readlines()

    # some articles has only 1 line, so write first into an array later filter them
    articles = [[]]

    article_start = False
    # process line by line
    for line in content:
        line = line.strip()

        # ignore empty line
        if not line:
            continue
        # ignore article start
        if line.startswith('<doc'):
            article_start = True
            continue
        # after article start, there is the article title, ignore it
        if article_start:
            article_start = False
            continue
        # ignore categories
        if line.startswith('[['):
            continue
        if line.startswith('</doc>'):
            articles.append([])
            continue
        # tokenize the news article sentence by sentence
        for sentence in sentence_tokenize(line):
            articles[-1].append(sentence)

    # we need articles with at least 2 lines
    articles = [d for d in articles if len(d) >= 2]

    # write into a single file
    with open(join(MN_CORPUS_FOLDER, MN_WIKI_FILE), 'a') as f:
        for article in articles:
            for sentence in article:
                f.write(sentence)
                f.write('\n')
            # extra new line to separate each news articles
            f.write('\n')


# pre process the extracted news files
print('%s/*/*.txt' % MN_WIKI_EXTRACT_FOLDER)
for file_name in glob.glob('%s/*/wiki_*' % MN_WIKI_EXTRACT_FOLDER):
    _pre_process(file_name)
print("done!")
