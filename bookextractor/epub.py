import sys
import os
import ebooklib
from ebooklib import epub

if (len(sys.argv)>1):
    bookpath = sys.argv[1]
    book = epub.read_epub(bookpath)
    for image in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        print(image)
    pass
