#!/usr/bin/env python3
"""Pre processed a epub converted by Calibre.
Use following options to convert with Calibre:
  -
"""
__author__ = 'Sharavsambuu, Erdene-Ochir Tuguldur'

import re
import sys
from os.path import exists, join, dirname
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


def _process_section(section):
    content = section.get_content().decode("utf-8")
    soup = BeautifulSoup(content, 'html.parser')

    lines = []
    children = soup.find('body').findChildren()
    for child in children:
        if child.name == 'p':
            lines.append(EMPTY_LINE)
        elif child.name == 'div' and child.get('class') is not None and 'calibre2' in child.get('class'):
            line = child.text.strip()
            if len(line) > 0:
                lines.append(line)
    if len(lines) >= 2:
        lines = _unwrap_lines(lines)
    lines = [_process_line(line) for line in lines]
    lines.append(EMPTY_LINE)

    sentences = []
    for line in lines:
        sentences += sentence_tokenize(line)

    return sentences


def _process_calibre_epub(file_name):
    print("pre processing '%s'..." % file_name)
    book = epub.read_epub(file_name)

    sentences = []
    for (section, _) in book.spine:
        print("\tpre processing '%s'..." % section)
        sentences += _process_section(book.get_item_with_id(section))

    # sanity check
    if len([s for s in sentences if s != EMPTY_LINE]) < 100:
        print("Warning too few sentences!")
        sys.exit(1)

    # grouped sentences
    grouped_sentences = [[]]
    for sentence in sentences:
        if sentence == EMPTY_LINE:
            grouped_sentences.append([])
        else:
            grouped_sentences[-1].append(sentence)
    # at least 2 sentences
    grouped_sentences = [s for s in grouped_sentences if len(s) >= 2]

    title = re.sub(r"\s+", '_', book.title.lower().strip())
    output_file_name = join(MN_BOOK_CORPUS_DIR, '%s.txt' % title)
    print("saving into: '%s'" % output_file_name)
    if exists(output_file_name):
        print("'%s' already exists!" % output_file_name)
        sys.exit(1)

    total = 0
    with open(output_file_name, 'w') as output_file:
        for sentences in grouped_sentences:
            for sentence in sentences:
                total += 1
                output_file.write(sentence)
                output_file.write('\n')
            output_file.write('\n')

    print('Done: %i lines\n' % total)


if __name__ == "__main__":
    # import sys, doctest; doctest.testmod(); sys.exit(0)

    _process_calibre_epub(sys.argv[1])
