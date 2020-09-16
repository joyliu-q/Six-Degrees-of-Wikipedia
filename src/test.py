import requests
import urllib.request
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen

import numpy as np
import json
import time 
import sys

# Experimenting with using MediaWiki API instead of BS4 url grab
# avg time: 0.3 - 0.8 s, which is still kind of a feels-bad when ea page has 300-500 links
# 100 trials: 30.61058211326599 s
start = time.time()
for i in range(1):
    response = urlopen("https://en.wikipedia.org/w/api.php?action=query&titles=" + "Title" + "&prop=links&pllimit=max&format=json")
    dab = time.time()
    DATA = json.loads(response.read())
    print(DATA)
    #print(json.dumps(DATA, indent=4, sort_keys=True))
print(time.time() - dab)

# Normal/Old method: using BS4: average ime 0.5-0.6. 
# 100 trials: 60.8656702041626 s
"""
start = time.time()
only_a_tags = SoupStrainer("a", href=lambda href: href and href.startswith('/wiki/'))
for i in range(100):
    response = urlopen("https://en.wikipedia.org/wiki/Bacon")
    soup = BeautifulSoup(response, 'html.parser', parse_only = only_a_tags)
print(time.time() - start)
"""