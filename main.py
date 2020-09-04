import requests
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen

# Set-Up
url = 'https://en.wikipedia.org/wiki/Kevin_Bacon'
html = urlopen(url) 
soup = BeautifulSoup(html, 'html.parser')

soup = soup.find_all("a", href=lambda href: href and href.startswith('/wiki/'))
relevant_entries = {}

def collect_data(current_soup):
    for entry in current_soup:
        #print(entry.contents[0])
        #print(entry["href"])
        if str(entry.contents) != "[]":
            if "[<" in entry.contents[0] or entry.contents[0] == None:
                continue
            else:
                relevant_entries[entry.contents[0]] = entry["href"]
    print(relevant_entries)
