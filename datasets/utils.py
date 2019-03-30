"""Utility methods."""
__author__ = 'Erdene-Ochir Tuguldur'

import sys
import math
import requests
from tqdm import tqdm
import nltk
from nltk import tokenize

# this line is needed for tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def download_file(url, file_path):
    """Downloads a file from the given URL."""
    print("downloading %s..." % url)
    r = requests.get(url, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 * 1024
    wrote = 0
    with open(file_path, 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size // block_size), unit='MB'):
            wrote = wrote + len(data)
            f.write(data)

    if total_size != 0 and wrote != total_size:
        print("downloading failed")
        sys.exit(1)


def sentence_tokenize(text):
    """Sentence tokenizer"""
    return tokenize.sent_tokenize(text)
