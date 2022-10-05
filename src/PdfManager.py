import PyPDF2
import codecs

from textblob import TextBlob

#create file object variable
#opening method will be rb


class ReadingProgressTracker:
    def __init__(self, user_id):
        self._user_id = user_id
        self._current_tracking_index = 0
        self._text = ""


def text_cleanup(text: str) -> str:
    cleaned_text = " ".join([word for word in str(text).split()])
    textblb = TextBlob(cleaned_text)
    corrected_text = textblb.correct()
    # return clean_text
    return str(corrected_text)


if __name__ == "__main__":
    # windows os sample filename
    # sampleFileName = "C:\\Users\\vp\\Documents\\books\\Dive_Into_Design_Patterns.pdf"

    # unix os sample filename
    sampleFileName = "C:\\Users\\vp\\Documents\\books\\Dive_Into_Design_Patterns.pdf"
    try:
        pdffileobj = open(sampleFileName, "rb")
    except Exception as e:
        print(e)
        exit(1)

    pdfreader = PyPDF2.PdfFileReader(pdffileobj)
    total_pages_quantity = pdfreader.numPages

    for i in range(total_pages_quantity):
        pageobj = pdfreader.getPage(i)
        try:
            # text = pageobj.extractText().encode("utf-8")
            text = pageobj.extractText()
        except Exception as e:
            print(e)
            continue

        # TODO: solve problem with artifact chars and encoding
        with open("result_text.txt", "a", encoding="utf-8") as result_file:
            clean_text = text_cleanup(str(text))
            result_file.write(clean_text + '\n')