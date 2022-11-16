# this approach can't handle nbsp
# from epub2txt import epub2txt


# class EpubManager:
#     @staticmethod
#     def translateEpubToTxt(file):
#         return epub2txt(file)


# from epub2txt import epub2txt


# class EpubManager:
#     @staticmethod
#     def translateEpubToTxt(file):
#         return epub2txt(file)


import ebooklib

from ebooklib import epub
from bs4 import BeautifulSoup
from cleantext import clean


def to_text(html_item):
    soup = BeautifulSoup(html_item.get_body_content(), 'html.parser')
    text = [para.get_text() for para in soup.find_all('p')]
    return ' '.join(text)


class EpubManager:
    @staticmethod
    def translateEpubToTxt(file):
        book = epub.read_epub(file)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        raw_text = " ".join([to_text(item) for item in items])
        return raw_text.replace("\n", " ")

        # return epub2txt(file)
