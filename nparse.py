from collections import Counter
import pandas as pd
from dateutil.parser import parse
import re
from lxml import html
import glob

def trim(x):
    return x.rstrip().lstrip()

def parse_date(x):
    return parse(x, dayfirst=True)

class Post:
    def __init__(self, author, date_str, lines, keyValues, fname):
        self.author = author
        self.date_str = date_str.replace('»','')
        self.lines = lines
        self.key_vals = keyValues
        self.fname = fname
    def __str__(self):
        return "[author=%s, date=%s, key_vals=%s]" % (self.author, self.date_str, self.key_vals)
    def extract(self):
        keywords = set([x.lower() for x in ['Date of application','Date of approval','Date of Ceremony']])
        ret = dict()
        ret['fname'] = self.fname
        ret['author'] = self.author
        ret['post_date'] = parse_date(self.date_str).isoformat()
        for k in self.key_vals.keys():
            v = self.key_vals[k]
            kword = trim(k).lower()
            if kword in keywords and len(trim(v)) > 6:
                try:
                    date = parse_date(trim(v))
                    ret[kword] = date.isoformat()
                except ValueError as e:
                    pass
        return ret



def parse_post(post, fname):
    author = post.xpath('./p[@class="author"]/strong/a/text()')
    if len(author) != 1:
        return None
    author = author[0]
    date_str = post.xpath('./p[@class="author"]/text()')[1]
    lines = post.xpath('./div[@class="content"]//text()')
    d = dict()
    for line in lines:
        m = re.search('([^:]+):(.*)', line)
        if m:
            d[m.group(1)]=m.group(2)
    return Post(author, date_str, lines, d, fname)

def parse_file(fname):
    body = open(fname).read()
    tree = html.fromstring(body)
    posts = tree.xpath('//div[@class="postbody"]')
    parsed_posts = [parse_post(x, fname) for x in posts]
    return parsed_posts

def flatten(l):
    return [item for sublist in l for item in sublist]

all_posts = [parse_file(fname) for fname in glob.glob('*.html')]
posts = flatten(all_posts)
items = [p.extract() for p in posts if p]
pd.DataFrame.from_records(items).to_csv('result.csv')
cnt = Counter([trim(p).lower() for p in flatten([x.key_vals.keys() for x in posts if x])])
for x in cnt.most_common(50):
    print(x)
