#!/usr/bin/env python3
"""Download and pre process the 700 million word Mongolian news data set."""
__author__ = 'Erdene-Ochir Tuguldur'

import os
import glob
import requests
import patoolib
from os.path import exists, join
from utils import download_file, sentence_tokenize

MN_NEWS_700M_FILE = 'mn_news_700m_%i.txt'
MN_CORPUS_FOLDER = 'mn_corpus'
MN_NEWS_700M_RAR_FILE = 'mn_news_700m.rar'
MN_NEWS_700M_EXTRACT_FOLDER = 'tmp_mn_news_700m'
MN_NEWS_700M_URL = 'https://yadi.sk/d/z5e3MVnKvFvF6w'


# create corpus directory
if not exists(MN_CORPUS_FOLDER):
    os.makedirs(MN_CORPUS_FOLDER)

if not exists(MN_NEWS_700M_RAR_FILE):
    print('downloading %s...' % MN_NEWS_700M_RAR_FILE)
    url = requests.get('https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key=%s'
                       % MN_NEWS_700M_URL).json()['href']
    print('download url is %s...' % url)
    download_file(url, MN_NEWS_700M_RAR_FILE)

# extract unrar
if not os.path.exists(MN_NEWS_700M_EXTRACT_FOLDER):
    os.makedirs(MN_NEWS_700M_EXTRACT_FOLDER)
patoolib.extract_archive(MN_NEWS_700M_RAR_FILE, outdir=MN_NEWS_700M_EXTRACT_FOLDER)


def _pre_process(news_file_name, output_file):
    """a very simple pre processing"""
    print("pre processing '%s'..." % news_file_name)
    with open(news_file_name) as f:
        content = f.readlines()

    print("writing into '%s'..." % output_file)
    with open(output_file, 'a') as f:
        # each line as a news article
        for news in content:
            news = news.strip()

            # if the news article is too short ignore it
            if len(news) < 150:
                continue

            # tokenize the news article sentence by sentence
            sentences = sentence_tokenize(news)
            # we need at least 6 lines, because we are going to remove the first and the last sentences
            # because they contain sometimes author, date and so on.
            if len(sentences) >= 6:
                for sentence in sentences[1:-1]:
                    f.write(sentence)
                    f.write('\n')
                # extra new line to separate each news articles
                f.write('\n')


# pre process the extracted news files
for idx, file_name in enumerate(sorted(glob.glob('%s/*.txt' % MN_NEWS_700M_EXTRACT_FOLDER))):
    _pre_process(file_name, join(MN_CORPUS_FOLDER, MN_NEWS_700M_FILE % (idx + 1)))
print("done!")
