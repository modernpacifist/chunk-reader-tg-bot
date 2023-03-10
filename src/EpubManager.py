import ebooklib
import logging

from ebooklib import epub
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

EPUB_TAG_BLACKLIST = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head',
    'input',
    'script',
    ]


def epub2html(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


def html2ttext(thtml):
    Output = []
    for html in thtml:
        text = chap2text(html)
        Output.append(text)
    return Output


def chap2text(chap):
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in EPUB_TAG_BLACKLIST:
            output += '{} '.format(t)
    return output


def epub2text(epub_path):
    chapters = epub2html(epub_path)
    ttext = html2ttext(chapters)
    return ttext


class EpubManager:
    @staticmethod
    def translateEpubToTxt(file):
        try:
            return " ".join(epub2text(file))

        except Exception as e:
            LOGGER.error(e)
