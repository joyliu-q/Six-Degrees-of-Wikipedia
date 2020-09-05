import requests
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen

# Dismissed links are links shared by all sites and do not factor into 6 degrees of separation
dismissed_links = ["Talk", "Categories", "Contributions", "Article", "Read", "Main page", "Contents", "Current events", "Random article", "About Wikipedia", "Help", "Community portal", "Recent changes", "Upload file", "What links here", "Related changes", "Upload file", "Special pages", "About Wikipedia", "Disclaimers", "Articles with short description", "Short description matches Wikidata", "Wikipedia indefinitely semi-protected biographies of living people", "Use mdy dates from October 2016", "Articles with hCards", "BLP articles lacking sources from October 2017", "All BLP articles lacking sources", "Commons category link from Wikidata", "Articles with IBDb links", "Internet Off-Broadway Database person ID same as Wikidata", "Short description is different from Wikidata"] 
degree = 1

# find_connections - A function that returns all relevant referrals by Wikipedia
def return_connections(url):
    html = urlopen(url) 
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find_all("a", href=lambda href: href and href.startswith('/wiki/'))

    relevant_entries = {}

    for entry in soup:
        if str(entry.contents) != "[]":
            if "Wikipedia articles with" in entry.contents[0] or "[<" in entry.contents[0] or "<" in str(entry.contents[0]) or entry.contents[0] == None:
                continue
            else:
                if entry.contents[0] in dismissed_links:
                    continue
                relevant_entries[entry.contents[0]] = entry["href"]
    return relevant_entries

# Supplementl function for determine_degrees()
def find_common(entries1, entries2):
    url1_keys = set(entries1.keys())
    url2_keys = set(entries2.keys())
    intersection = {}
    for key in url1_keys.intersection(url2_keys): 
        intersection[key] = entries1[key]
    return intersection

# Determine amount of degrees and commonalities, with origin and end being urls
def determine_degrees(origin, end):
    # Check degree
    global degree
    origin_connections = return_connections(origin)
    end_connections = return_connections(end)
    shared_connections = find_common(origin_connections,end_connections)

    # If there are shared connections, return
    if len(shared_connections) != 0:
        print(shared_connections)
        return [degree, shared_connections]
    # Otherwise, raise degree and keep searching
    degree += 1
    for entry_o in origin_connections:
        for entry_e in end_connections:
            determine_degrees("https://en.wikipedia.org" + entry_o["href"], "https://en.wikipedia.org" + entry_e["href"])

degree_info = determine_degrees("https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon", "https://en.wikipedia.org/wiki/Shrek")

print(str(degree_info[0]) + "\n" + str(degree_info[1]))