from epub2txt import epub2txt


class EpubManager:
    @staticmethod
    def translateEpubToTxt(file):
        return epub2txt(file)
