from enum import Enum


class common():
    class source(Enum):
        unknown=0
        ficsave=1   # http://ficsave.xyz/
        flagfic=2   # https://flagfic.net/
        ao3=3       # https://archiveofourown.org/
        ff2ebook=5  # http://ff2ebook.com/
        ficlab=6    # https://www.ficlab.com/
        custom=7    # Another app we made, some other extractor
        fuchub=8    # https://fichub.net/

# static
class SourceFinder():

    @staticmethod
    def get_source(epub_data):
        '''[to-do] Return the source-type of the provided epub
        args:
            epub_data(dict): Dictionary representation of the epub file
                             containing extracted data in the same folder-
                             hierarchy as was present in the original 
                             zipped ebook.'''
        origin = common.source.unknown
        return origin
