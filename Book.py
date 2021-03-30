
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, SoupStrainer
import requests
import os.path
import datetime


class Book:
  @classmethod
  def process_file(cls, filename):
    ebook = epub.read_epub(filename)
    for item in ebook.get_items():
      if item.get_type() == ebooklib.ITEM_DOCUMENT:
        content = item.get_content()
        soup = BeautifulSoup(content, features="lxml")
        return cls.process(ebook, soup, item, filename)

  @classmethod
  def process(cls, ebook, soup, item, filename):
    body = soup.body.text
    if 'URL:' in body:
      book = AltBook(ebook)
      book.ebook = ebook
      book.source_filename = filename
      book.process_body(body)
      # if 'fanfiction.net' in book.source_url or 'archiveofourown.org' in book.source_url:
      #   book.check_source_date()
      return book
    elif 'archiveofourown.org' in body:
      book = AO3Book(ebook)
      book.source_filename = filename
      book.process_body(body)
      return book
    else:
      book = FF2EbookBook(ebook)
      book.source_filename = filename
      book.process_body(body, item)
      return book

  def __init__(self, ebook):
    self.ebook = ebook
    self.title = ebook.title.replace(',', '-')
    self.author = ''
    self.fandom = ''
    self.last_update_date = ''
    self.word_count = 0
    self.summary = ''
    self.source_url = ''
    self.source_update_date = ''
    self.source_filename = ''

  @staticmethod
  def parse_date(date_string):
    parse_strings = ['%d %b %Y', '%m/%d/%Y', '%b %d', '%m/%d']
    test_date = None
    if date_string is None:
      date_string = ''
    for parse_string in parse_strings:
      try:
        test_date = datetime.datetime.strptime(date_string, parse_string).date()
        if test_date.year == 1900:
          test_date = test_date.replace(year=datetime.datetime.today().year)
      except ValueError:
        pass
    if test_date is None:
      if 'h' in date_string:
        delta = datetime.timedelta(hours=int(date_string.replace('h', '')))
        test_date = datetime.datetime.today() - delta
      else:
        return date_string
    return test_date.strftime('%Y-%m-%d')

  def write_to_csv(self, filename):
    line = '{},{},{},{},{},{},{},"{}"'.format(self.title, self.author, self.fandom,
                                              self.last_update_date, self.source_update_date,
                                              self.word_count, self.source_url, self.summary)
    with open(filename, 'a') as out_file:
      try:
        out_file.write(line)
      except UnicodeEncodeError:
        print(f"ERROR: {self.title}")
      out_file.write('\n')


class FF2EbookBook(Book):
  def process_body(self, body, item):
    line_map = self.extract_line_map(body)
    if 'summary' in line_map:
      self.process_line_map(line_map)
    else:
      self.process_missing()
    self.extract_source_url(item)
    # self.check_source_date()

  def extract_source_url(self, item):
    body = item.get_body_content()
    try:
      strainer = BeautifulSoup(body, parse_only=SoupStrainer('a'), features="lxml")
      link = strainer.find_all('a')[0].attrs['href']
      self.source_url = link
    except Exception:
      self.source_url = ''

  @staticmethod
  def extract_line_map(body):
    line_map = {}
    lines = body.split('\n')
    for full_line in lines:
      line = full_line.strip()
      if line:
        if ':' in line and not line.startswith(' '):
          parts = line.split(':')
          key = parts[0]
          value = ':'.join(parts[1:])
          if ',' in value:
            value = value.replace(',', '')
          if len(parts) > 1:
            line_map[key.lower().strip()] = value.strip()
        else:
          not_keyed = line_map.get('NOT_KEYED')
          if not_keyed is None:
            not_keyed = []
            line_map['NOT_KEYED'] = not_keyed
          not_keyed.append(line)
    return line_map

  def process_line_map(self, line_map):
    self.author = line_map.get('by')
    self.fandom = line_map.get('fandom')
    self.last_update_date = self.parse_date(line_map.get('last updated'))
    word_count = line_map.get('words count')
    if not word_count:
      word_count = line_map.get('words')
    if word_count:
      self.word_count = int(word_count)
    self.summary = line_map.get('summary')

  def process_missing(self):
    pass

  def check_source_date(self):
    # page = requests.get(self.source_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tags = soup.find_all('span')
    update_date = None
    for tag in tags:
      if tag.attrs.get('data-xutime') is not None:
        update_date = tag.text
        break
    if update_date is None:
      self.source_update_date = ''
    else:
      self.source_update_date = self.parse_date(update_date)


class AO3Book(Book):
  def process_body(self, body):
    lines = body.split('\n')
    new_lines = []
    index = 0
    while index < len(lines):
      line = lines[index].strip()
      if line:
        if line.endswith(':'):
          line = line, lines[index + 1]
          index += 1
        new_lines.append(line)
      index += 1
    for line in new_lines:
      if 'archiveofourown.org' in line:
        url = line.split('http://')
        url = 'http://{}'.format(url[1])
        if url.endswith('.'):
          url = url[:-1]
        self.source_url = url
      elif ':' in line:
        parts = line.split(':')
        if len(parts) == 2:
          key = parts[0].strip()
          value = parts[1].strip()
          if key == 'Fandom':
            self.fandom = value.split(',')[0]
          if key == 'Updated' or key == 'Completed':
            self.last_update_date = self.parse_date(value)
          if key == 'Words':
            self.word_count = int(value)
    # self.check_source_date()

  def check_source_date(self):
    headers = {'user-agent': 'Chrome/52 (Macintosh; Intel Mac OS X 10_10_5); Jingyi Li/UC Berkeley/email@address.com'}
    # page = requests.get(self.source_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    tags = soup.find_all('p')
    update_date = None
    for tag in tags:
      if tag.attrs.get('class') is not None:
        if 'datetime' in tag.attrs['class']:
          update_date = tag.text
          break
    if update_date is None:
      tags = soup.find_all('dd')
      update_date = None
      for tag in tags:
        if tag.attrs.get('class') is not None:
          if 'status' in tag.attrs['class']:
            update_date = tag.text
            break
    if update_date is None:
      self.source_update_date = ''
    else:
      self.source_update_date = self.parse_date(update_date)
    self.check_source_other_ao3(soup)

  def check_source_other_ao3(self, soup):
    if not self.summary:
      tags = soup.find_all('blockquote')
      for tag in tags:
        if tag.attrs.get('class') is not None:
          if 'summary' in tag.attrs['class'] or 'userstuff' in tag.attrs['class']:
            self.summary = tag.text.strip().replace('\n', ' - ')
            break
    if not self.author:
      tags = soup.find_all('a')
      for tag in tags:
        if tag.attrs.get('rel') is not None:
          if 'author' in tag.attrs['rel']:
            self.author = tag.text.strip()
            break
    if not self.fandom:
      tags = soup.find_all('h5')
      for tag in tags:
        if tag.attrs.get('class') is not None:
          if 'fandoms' in tag.attrs['class']:
            self.fandom = tag.text.strip().replace('\n', '')
            break
    if not self.fandom:
      tags = soup.find_all('dd')
      for tag in tags:
        if tag.attrs.get('class') is not None:
          if 'fandom' in tag.attrs['class']:
            self.fandom = tag.text.strip().replace('\n', '')
            break
    if self.fandom.startswith('Fandom'):
      self.fandom = ':'.join(self.fandom.split(':')[1:])
    self.fandom = self.fandom.replace(',', '-')


class AltBook(AO3Book, FF2EbookBook):
  def process_body(self, body):
    lines = body.split('\n')
    new_lines = []
    for line in lines:
      if line.strip():
        new_lines.append(line.strip())
    temp = new_lines[1].split(' ')
    self.author = ' '.join(temp[1:])
    self.fandom = '?'
    special_line = new_lines[3]
    parts = special_line.split('-')
    self.word_count = '?'
    self.last_update_date = '?'
    for part in parts:
      sub_parts = part.split(':')
      if len(sub_parts) > 1:
        key = sub_parts[0].strip()
        value = sub_parts[1].strip()
        if key == 'Words':
          self.word_count = int(value.replace(',', ''))
        if key == 'Updated':
          self.last_update_date = self.parse_date(value)
    self.summary = new_lines[2]
    self.source_url = ':'.join(new_lines[4].split(':')[1:])
    # if 'fanfiction.net' in self.source_url or 'archiveofourown.org' in self.source_url:
    #   self.check_source_date()

  def check_source_date(self):
    if not self.source_url:
      return
    if 'fanfiction.net' in self.source_url:
      FF2EbookBook.check_source_date(self)
    elif 'archiveofourown.org' in self.source_url:
      AO3Book.check_source_date(self)


EXPORT_FILENAME = 'Fanfic_Summaries.txt'

print('Scanning')

directory = './epubs/'
if os.path.isfile(EXPORT_FILENAME):
  os.remove(EXPORT_FILENAME)

dir_list = list(os.scandir(directory))
for entry_index, entry in enumerate(dir_list):
  if entry.is_file() and entry.path.endswith('epub'):
    try:
      the_book = Book.process_file(entry.path)
      the_book.write_to_csv(EXPORT_FILENAME)
      print('  Processed {}/{} - {}'.format(entry_index + 1, len(dir_list), the_book.title))
    except Exception:
      print(f'error with book: {entry.path}')
      continue
    

# book = Book()
# book.process_file('epubs/Amelia By TanaNari.epub')
print('Done')
