import sys
import os
import ebooklib
from ebooklib import epub
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        print(data)

parser = MyHTMLParser()

if (len(sys.argv)>1):
    bookpath = sys.argv[1]
    book = epub.read_epub(bookpath)
    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = doc.get_content().decode("utf-8") 
        content = parser.feed(content)
        print(content)
    pass
