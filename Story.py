'''Holds the story class and some epub structure information'''

from source_finder import common, SourceFinder
from zipfile import ZipFile
import settings

class Story:
    '''Handles interfacing with epub files'''

    def __init__(self):
        '''Initialize story parameters'''
        self.title = ""
        self.author = ""
        self.summary = ""
        self.chapter_count = 0
        self.category = ""
        self.word_count = 0
        self.review_count = 0
        self.favorite_count = 0
        self.follow_count = 0
        self.update_date = ""
        self.publish_date = ""
        self.status = ""
        self.series = []
        self.story_id = ""
        self.story_link = ""
        self.rating = 0
        self.comments = ""

    def load_story(self, path):
        '''[to-do] parses epub file into story'''
        # need to start by loading up the file
        epub_data = self._open_epub(path)
        
        # then we need to determine the source of the story.
        origin = SourceFinder.get_source(epub_data)
        # if the origin is parseable, load up a parser to handle
        # grabbing the story info
        print(origin)
    
    def _open_epub(self, path):
        book = ZipFile(path)
        return {name: book.read(name) for name in book.namelist()}