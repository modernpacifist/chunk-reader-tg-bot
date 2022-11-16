import ebooklib

from ebooklib import epub
from bs4 import BeautifulSoup
from cleantext import clean
from epub2txt import epub2txt


def to_text(html_item):
    soup = BeautifulSoup(html_item.get_body_content(), 'html.parser')
    text = [para.get_text() for para in soup.find_all('p')]
    return ' '.join(text)


class EpubManager:
    @staticmethod
    def translateEpubToTxt(file):
        try:
            return epub2txt(file)

        except Exception as e:
            print(e)
            book = epub.read_epub(file)
            items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            raw_text = " ".join([to_text(item) for item in items])
            return raw_text.replace("\n", " ")
