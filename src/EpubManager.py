from epub2txt import epub2txt

#create file object variable
#opening method will be rb


class EpubManager:
    @staticmethod
    def translateEpubToTxt(file):
        return epub2txt(file)


if __name__ == "__main__":
    # url = "https://github.com/ffreemt/tmx2epub/raw/master/tests/1.tmx.epub"
    # res = Epub2txt(url)
    # print(res)

    filepath = r"C:\\Users\\vp\\Downloads\\1.tmx.epub"
    with open(filepath) as file:
        res = EpubManager.translateEpubToTxt(filepath)
    print(res[:100])