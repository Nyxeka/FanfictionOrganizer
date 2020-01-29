'''Holds the story class and some epub structure information'''


class Story:
    '''Handles interfacing with epub files'''

    __init__(self):
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
        pass
