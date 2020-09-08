import requests
import urllib.request, json
from bs4 import BeautifulSoup, SoupStrainer
import numpy as np
from urllib.request import urlopen
import time 
import sys

# Experimenting with using MediaWiki API instead of BS4 url grab
# avg time: 0.3 - 0.8 s, which is still kind of a feels-bad when ea page has 300-500 links
# 100 trials: 30.61058211326599 s
start = time.time()
for i in range(100):
    response = urlopen("https://en.wikipedia.org/w/api.php?action=query&titles=" + "Title" + "&prop=links&pllimit=max&format=json")
    dab = time.time()
    DATA = json.loads(response.read())
    print(time.time() - dab)
print(time.time() - start)

# Normal/Old method: using BS4: average ime 0.5-0.6. 
# 100 trials: 60.8656702041626 s
start = time.time()
only_a_tags = SoupStrainer("a", href=lambda href: href and href.startswith('/wiki/'))
for i in range(100):
    response = urlopen("https://en.wikipedia.org/wiki/Bacon")
    soup = BeautifulSoup(response, 'html.parser', parse_only = only_a_tags)
print(time.time() - start)
