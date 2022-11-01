# this approach can't handle nbsp
# from epub2txt import epub2txt


# class EpubManager:
#     @staticmethod
#     def translateEpubToTxt(file):
#         return epub2txt(file)
from epub2txt import epub2txt


class EpubManager:
    @staticmethod
    def translateEpubToTxt(file):
        return epub2txt(file)
