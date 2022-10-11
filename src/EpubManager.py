import PyPDF2
import codecs

from textblob import TextBlob

from epub2txt import epub2txt

#create file object variable
#opening method will be rb


def cleanup_text(text: str) -> str:
    cleaned_text = " ".join([word for word in str(text).split()])
    textblb = TextBlob(cleaned_text)
    corrected_text = textblb.correct()
    # return clean_text
    return str(corrected_text)


if __name__ == "__main__":
    # url = "https://github.com/ffreemt/tmx2epub/raw/master/tests/1.tmx.epub"
    # res = Epub2txt(url)
    # print(res)

    filepath = r"C:\Users\vp\Downloads"
    res = epub2txt(filepath)
    print(res)