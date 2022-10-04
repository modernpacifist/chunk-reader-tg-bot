import PyPDF2
 
#create file object variable
#opening method will be rb


if __name__ == "__main__":
    try:
        pdffileobj = open('1.pdf', 'rb')
    except Exception as e:
        print(e)

    pdfreader = PyPDF2.PdfFileReader(pdffileobj)
    total_pages_quantity = pdfreader.numPages
    
    for i in range(total_pages_quantity):
        pageobj = pdfreader.getPage(i)
        text = pageobj.extractText()

        file1 = open(r"result_text.txt", "a")
        file1.writelines(text + '\n')
        print(text)