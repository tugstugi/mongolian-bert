import sys
import os
import re
import ebooklib
from ebooklib import epub
import nltk
from nltk import tokenize
from bs4 import BeautifulSoup

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def should_preprocess(soup):
    """ rules 
        - shouldn't contain copyright notice : ©
        - shouldn't contain bookstore.mn
        - shouldn't contain 'contact' or 'buy' class elements
    """
    text_content = soup.get_text()
    if "©" in text_content:
        return False
    if "bookstore.mn" in text_content:
        return False
    classes = [value 
            for element in soup.find_all(class_=True)
            for value in element["class"]]
    if "buy" in classes or "contact" in classes:
        return False
    return True

def clean_html(soup):
    for class_name in ["text-center-bold", "text-center", "text-right-italic", "text-left-italic"]:
        for div in soup.find_all("div", {'class':class_name}):
            div.decompose()
        for p in soup.find_all("p", {'class':class_name}):
            p.decompose()
    return soup.get_text()

def preprocess(text):
    #text = re.sub(r'\n\s*\n', '\n\n', text)
    #return text
    sentences = tokenize.sent_tokenize(text)
    #for sent in sentences:
    #    pass
        #print(sent)
    #sentences = [sent.replace('\r\n', ' ') for sent in sentences]
    return sentences

texts = ""

def get_spine_key(book):
    spine_keys = {id:(ii,id) for (ii,(id,show)) in enumerate(book.spine)}
    past_end   = len(spine_keys)
    return lambda itm: spine_keys.get(itm.get_id(), (past_end,itm.get_id()))


if (len(sys.argv)>1):
    bookpath = sys.argv[1]
    book     = epub.read_epub(bookpath)

    for item in sorted([(get_spine_key(book)(itm), itm) for itm in book.get_items() if itm.get_type()==ebooklib.ITEM_DOCUMENT]):
        doc          = item[1]
        html_content = doc.get_content().decode("utf-8") 
        soup         = BeautifulSoup(html_content, 'html.parser')
        if not should_preprocess(soup):
            continue
        if soup is not None:
            text = clean_html(soup)
            text = preprocess(text)
            print(text)


    # reduce multiple empty lines to one
    #print(texts)
    pass
