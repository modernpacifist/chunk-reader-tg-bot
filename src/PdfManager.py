import PyPDF2
import codecs
 
#create file object variable
#opening method will be rb


if __name__ == "__main__":
    sampleFileName = "C:\\Users\\vp\\Documents\\books\\Dive_Into_Design_Patterns.pdf"
    try:
        pdffileobj = open(sampleFileName, "rb")
    except Exception as e:
        print(e)

    pdfreader = PyPDF2.PdfFileReader(pdffileobj)
    total_pages_quantity = pdfreader.numPages
    
    for i in range(total_pages_quantity):
        pageobj = pdfreader.getPage(i)
        try:
            text = pageobj.extractText().encode("utf-8")
        except Exception as e:
            print(e)
            continue

        # TODO: sovle problem with artifact chars and encoding
        with codecs.open("result_text.txt", "a", "utf-8-sig") as result_file:
            result_file.write(str(text) + '\n')

        print(text)