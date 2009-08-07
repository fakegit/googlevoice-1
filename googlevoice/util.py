import re
from sys import stdout
from xml.parsers.expat import ParserCreate
from pprint import pprint
try:
    from urllib2 import build_opener,install_opener, \
        HTTPCookieProcessor,Request,urlopen
    from urllib import urlencode,quote
except ImportError:
    from urllib.request import build_opener,install_opener, \
        HTTPCookieProcessor,Request,urlopen
    from urllib.parse import urlencode,quote
try:
    from http.cookiejar import LWPCookieJar as CookieJar
except ImportError:
    from cookielib import LWPCookieJar as CookieJar
try:
    from json import loads
except ImportError:
    from simplejson import loads
try:
    input = raw_input
except NameError:
    pass

sha1_re = re.compile(r'^[a-fA-F0-9]{40}$')

def print_(*s):
    stdout.write(''.join(map(str, s)))
    stdout.write('\n')
    stdout.flush()

def is_sha1(s):
    '''
    Returns True if the string is a SHA1 hash
    '''
    return bool(sha1_re.match(s))

class LoginError(Exception):
    '''
    Occurs when login credentials are incorrect
    '''
    
class ParsingError(Exception):
    '''
    Happens when XML feed parsing fails
    '''
    
class JSONError(Exception):
    '''
    Failed JSON deserialization
    '''
    
class DownloadError(Exception):
    '''
    Cannot download message, probably not in voicemail/recorded
    '''
    
class XMLParser(dict):
    '''
    XML Parser helper that can dig json and html out of the feeds
    Calling the parser returns a tuple of (data_dict, html_content)
    '''
    attr = None
    def start_element(self, name, attrs):
        if name in ('json','html'):
            self.attr = name
    def end_element(self, name): self.attr = None
    def char_data(self, data):
        if self.attr and data:
            self[self.attr] += data

    def __init__(self, data):
        dict.__init__(self, {'json':'', 'html':''})
        p = ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        try:
            p.Parse(data, 1)
        except:
            raise ParsingError

    def __call__(self):
        try:
            return loads(self['json']), self['html']
        except:
            raise JSONError