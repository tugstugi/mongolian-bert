#!/usr/bin/env python3
"""Pre processed a epub converted by Calibre.
Use following options to convert with Calibre:
  - Look & Feel -> Text -> Text justification -> Justify Text
  - Look & Feel -> Text -> Text justification -> Smarten punctuation
  - Heuristic processing -> Enable heuristic processing
  - Heuristic processing -> deselect Unwrap lines
  - Heuristic processing -> deselect Italicize common words and patterns
  - EPUB output -> Do not split on page breaks
  - EPUB output -> Flatten EPUB file structure
  - EPUB output -> Split files larger than 10000 KB
"""
__author__ = 'Sharavsambuu, Erdene-Ochir Tuguldur'

import re
import sys
from os.path import exists, join, dirname
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from utils import sentence_tokenize


mn_cyrillic = 'абвгдеёжзийклмноөпрстуүфхцчшъыьэюя'
mn_cyrillic_all = mn_cyrillic.upper() + mn_cyrillic


def _adjust_whitespaces(line):
    """Add or remove whitespace before or after '.,:!?'
    >>> _adjust_whitespaces('сайн уу ? Аль вэ   . байна! байна ! Аль: Аль : Аль , Аль,')
    'сайн уу? Аль вэ. байна! байна! Аль: Аль: Аль, Аль,'
    >>> _adjust_whitespaces('сайн байсан.Одоо байна?Одоо харцгааж :')
    'сайн байсан. Одоо байна? Одоо харцгааж:'
    """
    # хүү , -> хүү,
    line = re.sub(r"([%s]+)\s+([.,:!?])" % mn_cyrillic_all,
                  r"\1\2", line)
    # байсан.Одоо -> байсан. Одоо
    line = re.sub(r"([%s]+[.])([%s]+)" % (mn_cyrillic, mn_cyrillic.upper()),
                  r"\1 \2", line)
    line = re.sub(r"([%s]+[,:!?])([%s]+)" % (mn_cyrillic, mn_cyrillic_all),
                  r"\1 \2", line)
    return line


def _undo_wrong_word_breaks(line):
    """Undo wrong breaks.
    >>> _undo_wrong_word_breaks('зөвлөмж-  ийг хэрэг-жүүл- эх зорилго- Монгол')
    'зөвлөмжийг хэрэгжүүлэх зорилго- Монгол'
    """
    line = re.sub(r"([%s]+)-\s+([%s]+)" % (mn_cyrillic_all, mn_cyrillic), r"\1\2", line)
    line = re.sub(r"([%s]+)-([%s]+)" % (mn_cyrillic_all, mn_cyrillic), r"\1\2", line)
    return line


def _process_line(line):
    """Fix a line.
    >>> _process_line('Баруу-н зүүн- ээ хөшиглөн,хөндөлдөн дүнхийх.Намнан уулын өвөр Цагаан:бургас өглөө?нарнаар гараад яаралгүй сажилна.')
    'Баруун зүүнээ хөшиглөн, хөндөлдөн дүнхийх. Намнан уулын өвөр Цагаан: бургас өглөө? нарнаар гараад яаралгүй сажилна.'
    """
    return _undo_wrong_word_breaks(_adjust_whitespaces(line))


def _unwrap_lines(lines):
    """Unwrap lines.
    >>> _unwrap_lines(['single line'])
    ['single line']
    >>> _unwrap_lines(['line1', 'line2', 'line3'])
    ['line1', 'line2', 'line3']
    >>> _unwrap_lines(['байхаар хатуу', 'шийдсэн тухай'])
    ['байхаар хатуу шийдсэн тухай']
    >>> _unwrap_lines(['байхаар хатуу', 'Монгол Улсын'])
    ['байхаар хатуу', 'Монгол Улсын']
    >>> _unwrap_lines(['шийд-', 'сэн тухай', 'Тиймээс ч өчигдөр'])
    ['шийдсэн тухай', 'Тиймээс ч өчигдөр']
    >>> _unwrap_lines(['шийд-', 'сэн тухай', 'эх сурвалж өгүүлж байна.'])
    ['шийдсэн тухай эх сурвалж өгүүлж байна.']
    """
    unwrapped_lines = []
    current_line = lines[0].strip()
    for i in range(1, len(lines)):
        next_line = lines[i].strip()
        current_line_last_char = current_line.lower()[-1]
        next_line_first_char = next_line[0]
        if current_line_last_char in mn_cyrillic and next_line_first_char in mn_cyrillic:
            current_line = current_line + ' ' + next_line
        elif current_line_last_char == '-' and next_line_first_char in mn_cyrillic:
            current_line = current_line[:-1] + next_line
        else:
            unwrapped_lines.append(current_line)
            current_line = next_line
    unwrapped_lines.append(current_line)

    return unwrapped_lines


# use it to separate chapters, scene break and so on.
EMPTY_LINE = 'EMPTY_LINE'
# where to save the results
MN_BOOK_CORPUS_DIR = join(dirname(__file__), 'mn_book_corpus')


def _process_section(section, main_class):
    content = section.get_content().decode("utf-8")
    soup = BeautifulSoup(content, 'html.parser')

    lines = []
    children = soup.find('body').findChildren()
    for child in children:
        if child.get('class') is not None and main_class in child.get('class'):
            line = child.text.strip()
            if len(line) > 0:
                lines.append(line)
        else:
            lines.append(EMPTY_LINE)
    if len(lines) >= 2:
        lines = _unwrap_lines(lines)
    lines = [_process_line(line) for line in lines]
    lines.append(EMPTY_LINE)

    sentences = []
    for line in lines:
        sentences += sentence_tokenize(line)

    return sentences


def _detect_main_class(book):
    """Detect the most common CSS class."""
    css_classes = []
    for section in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = section.get_content().decode("utf-8")
        soup = BeautifulSoup(content, 'html.parser')
        children = soup.find('body').findChildren()
        for child in children:
            if child.get('class') is not None:
                css_classes += child.get('class')
    # return the most common css class
    return max(set(css_classes), key=css_classes.count)


def _process_calibre_epub(file_name):
    print("pre processing '%s'..." % file_name)
    book = epub.read_epub(file_name)
    title = re.sub(r"\s+", '_', book.title.lower().strip())
    title = title.replace('/', '_')
    print("  %s" % title)

    output_file_name = join(MN_BOOK_CORPUS_DIR, '%s.txt' % title)
    print("saving into: '%s'" % output_file_name)
    if exists(output_file_name):
        print("'%s' already exists!" % output_file_name)
        return

    # detect main CSS class, everything will be ignored
    main_class = _detect_main_class(book)

    sentences = []
    for section in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        print("\tpre processing '%s'..." % section)
        sentences += _process_section(section, main_class)

    # sanity check
    if len([s for s in sentences if s != EMPTY_LINE]) < 100:
        print("Warning for '%s': too few sentences!" % file_name)
        return

    # remove some lines
    def is_valid_line(l):
        return len(l) > 0 and not l.startswith('©') and 'store.mn' not in l
    sentences = [s for s in sentences if is_valid_line(s)]

    # grouped sentences
    grouped_sentences = [[]]
    for sentence in sentences:
        if sentence == EMPTY_LINE:
            grouped_sentences.append([])
        else:
            grouped_sentences[-1].append(sentence)
    # at least 2 sentences
    grouped_sentences = [s for s in grouped_sentences if len(s) >= 2]

    total = 0
    with open(output_file_name, 'w') as output_file:
        for sentences in grouped_sentences:
            for sentence in sentences:
                total += 1
                output_file.write(sentence)
                output_file.write('\n')
            output_file.write('\n')

    # sanity check
    if total < 20:
        print("Warning for '%s': too few sentences!" % file_name)

    print('Done: %i lines\n' % total)


if __name__ == "__main__":
    # import sys, doctest; doctest.testmod(); sys.exit(0)
    import glob
    for file_name in sorted(glob.glob('%s/*.epub' % sys.argv[1])):
        print(file_name)
        _process_calibre_epub(file_name)
