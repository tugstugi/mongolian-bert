import sys
import os
import re
import ebooklib
from ebooklib import epub
from html.parser import HTMLParser
import nltk
from nltk import tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

texts = ""

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        global texts
        texts = texts+"\n"
        sentences = tokenize.sent_tokenize(data)
        if len(sentences)!=0:
            for sentence in sentences:
                texts = texts + sentence+"\n"
                #print(sentence)

parser = MyHTMLParser()

if (len(sys.argv)>1):
    bookpath = sys.argv[1]
    book = epub.read_epub(bookpath)
    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = doc.get_content().decode("utf-8") 
        parser.feed(content)
    # reduce multiple empty lines to one
    texts = re.sub(r'\n\s*\n', '\n\n', texts)
    print(texts)
    pass
