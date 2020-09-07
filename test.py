import requests
import urllib.request
from bs4 import BeautifulSoup, SoupStrainer
import numpy as np
import pandas as pd
from urllib.request import urlopen
import time 
import sys
import concurrent
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future, as_completed, wait

start = time.time()
only_a_tags = SoupStrainer("a")
session = requests.Session()
print(time.time() - start)
response = urlopen("https://en.wikipedia.org/wiki/Little_Boxes")
print(time.time() - start)
soup = BeautifulSoup(response, 'html.parser', parse_only = only_a_tags)
soup = soup.find_all("a", href=lambda href: href and href.startswith('/wiki/'))

blah = 3

def test(meme):
    if meme == "2":
        return False
    print(meme)
    return True

list_a = ["wee", "1", "2"]
while blah != 0:
    with ThreadPoolExecutor(max_workers=2000) as executor:
        futures = [executor.map(test(item)) for item in list_a]
        for future in futures:
            print(future.result())