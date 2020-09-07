import requests
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen
import time 
import sys
import concurrent
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future 

# Changable Variables
USE_THREADPOOL = True

# Dismissed links are links shared by all sites and do not factor into 6 degrees of separation
dismissed_links = ["Talk", "Categories", "Contributions", "Article", "Read", "Main page", "Contents", "Current events", "Random article", "About Wikipedia", "Help", "Community portal", "Recent changes", "Upload file", "What links here", "Related changes", "Upload file", "Special pages", "About Wikipedia", "Disclaimers", "Articles with short description", "Short description matches Wikidata", "Wikipedia indefinitely semi-protected biographies of living people", "Use mdy dates from October 2016", "Articles with hCards", "BLP articles lacking sources from October 2017", "All BLP articles lacking sources", "Commons category link from Wikidata", "Articles with IBDb links", "Internet Off-Broadway Database person ID same as Wikidata", "Short description is different from Wikidata", "PMID", "ISBN", "doi"] 
degree = 0
path = []
path_found = False
current_generation = []
child_generation = []

class Node:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.parent = None
        self.children = []
        self.searched = False

    def get_url(self):
        return self.url

    # find_children - A function that returns all relevant referrals by Wikipedia
    def find_children(self):
        #start = time.time()
        html = urlopen(self.url) 
        soup = BeautifulSoup(html, 'html.parser')
        soup = soup.find_all("a", href=lambda href: href and href.startswith('/wiki/'))

        for entry in soup:
            if str(entry.contents) != "[]":
                if "/wiki/Help:" in entry.contents[0] or "Wikipedia articles with" in entry.contents[0] or "[<" in entry.contents[0] or "<" in str(entry.contents[0]) or entry.contents[0] == None:
                    continue
                else:
                    if entry.contents[0] in dismissed_links:
                        continue
                    # If relevant, add to entries
                    child_node = Node(entry.contents[0],"https://en.wikipedia.org" + entry["href"])
                    child_node.parent = self
                    self.children.append(child_node)
        #print(time.time() - start)           

def attempt_match_children(current_node, to_node):
    global path_found
    global child_generation
    global path 
    global USE_THREADPOOL

    if USE_THREADPOOL == False:
        current_node.find_children()
    current_node.searched = True

    # Check children for any matches w/ to_node 
    for child_node in current_node.children:
        # Check if child_node was already searched
        if child_node.searched == False:
            # Add child_node to new generation
            child_generation.append(child_node)
            # If child_node is the to_node, search is over
            if child_node.url == to_node.url:
                path.append(current_node)
                path.append(child_node)
                path_found = True
                return True
    return False

# Determine amount of degrees and commonalities, with origin and end being urls
def determine_path(from_node, to_node):
    global path_found
    global current_generation
    global path
    global degree
    global child_generation 
    global USE_THREADPOOL

    # 0th degree
    if from_node.url == to_node.url:
        path_found == True
        return path

    # 1st degree
    degree += 1
    from_node.find_children()
    attempt_match_children(from_node, to_node)

    # 2+ degree: if none of the children match, continue to search through loop
    if path_found == False:
        current_node = from_node
        current_generation = current_node.children
        path.append(current_node)

        while path_found == False: 
            degree += 1
            child_generation = []
            print(len(current_generation))

            # Special Threadpool to find children: attempt to stop BS4 from bottlenecking
            if USE_THREADPOOL == True:
                with ThreadPoolExecutor(max_workers=None) as executor:
                    [executor.submit(sibling_node.find_children()) for sibling_node in current_generation]
                print("yaw")

            # Keep Looping through each sibling_node and check sibling's children
            for sibling_node in current_generation:
                attempt_match_children(sibling_node, to_node)
                # If found match in current degree
                print(len(child_generation))
                if path_found == True:
                    return sibling_node

            # If none of the siblings in the level matched, move to higher degree
            if path_found == False:
                current_generation = child_generation
                child_generation = []

    return path


def main():
    global current_generation
    root = Node("Kevin Bacon", "https://en.wikipedia.org/wiki/Kevin_Bacon")
    current_generation.append(root)
    target = Node("Weeds (TV series)", "https://en.wikipedia.org/wiki/Weeds_(TV_series)")
    determine_path(root, target)
    print("Path:")
    for node in path:
        print(node.url)
    print("Degree: " + str(degree))

if __name__ == '__main__':
    main()
