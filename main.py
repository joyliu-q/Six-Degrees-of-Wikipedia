import requests
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen
import time 

# Dismissed links are links shared by all sites and do not factor into 6 degrees of separation
dismissed_links = ["Talk", "Categories", "Contributions", "Article", "Read", "Main page", "Contents", "Current events", "Random article", "About Wikipedia", "Help", "Community portal", "Recent changes", "Upload file", "What links here", "Related changes", "Upload file", "Special pages", "About Wikipedia", "Disclaimers", "Articles with short description", "Short description matches Wikidata", "Wikipedia indefinitely semi-protected biographies of living people", "Use mdy dates from October 2016", "Articles with hCards", "BLP articles lacking sources from October 2017", "All BLP articles lacking sources", "Commons category link from Wikidata", "Articles with IBDb links", "Internet Off-Broadway Database person ID same as Wikidata", "Short description is different from Wikidata", "PMID", "ISBN", "doi"] 
degree = 0
path = []

# find_connections - A function that returns all relevant referrals by Wikipedia
def return_connections(url):
    html = urlopen(url) 
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find_all("a", href=lambda href: href and href.startswith('/wiki/'))

    relevant_entries = {}

    for entry in soup:
        if str(entry.contents) != "[]":
            if "/wiki/Help:" in entry.contents[0] or "Wikipedia articles with" in entry.contents[0] or "[<" in entry.contents[0] or "<" in str(entry.contents[0]) or entry.contents[0] == None:
                continue
            else:
                if entry.contents[0] in dismissed_links:
                    continue
                # If relevant, add to entries
                relevant_entries[entry.contents[0]] = "https://en.wikipedia.org" + entry["href"]
    
    return relevant_entries

# Determine amount of degrees and commonalities, with origin and end being urls
def determine_degrees(origin_url, end_url):
    # Check degree
    global degree
    global path

    path.append(origin_url)

    origin_connections = return_connections(origin_url)

    # 1st degree: origin -> end
    #degree += 1
    print(origin_connections.values())
    if end_url in origin_connections.values():
        path.append(end_url)
        return path

    # 2nd degree: origin -> blah -> end
    #degree += 1
    print(len(origin_connections.values()))
    for entry in origin_connections.values(): 
        connections = return_connections(entry)
        if end_url in connections.keys():
            path.append(entry)
            path.append(end_url)
    
    # 3+ degree: origin -> ... -> end
    #degree += 1
    for entry in origin_connections.values(): 
        determine_degrees(entry, end_url)

degree_info = determine_degrees("https://en.wikipedia.org/wiki/Philosophical_Transactions_of_the_Royal_Society", "https://en.wikipedia.org/wiki/Kevin_Bacon")

print("Path: " + str(path))