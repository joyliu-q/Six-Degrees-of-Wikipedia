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

# Dismissed links are links shared by all sites and do not factor into 6 degrees of separation
dismissed_links = ["Talk", "Categories", "Contributions", "Article", "Read", "Main page", "Contents", "Current events", "Random article", "About Wikipedia", "Help", "Community portal", "Recent changes", "Upload file", "What links here", "Related changes", "Upload file", "Special pages", "About Wikipedia", "Disclaimers", "Articles with short description", "Short description matches Wikidata", "Wikipedia indefinitely semi-protected biographies of living people", "Use mdy dates from October 2016", "Articles with hCards", "BLP articles lacking sources from October 2017", "All BLP articles lacking sources", "Commons category link from Wikidata", "Articles with IBDb links", "Internet Off-Broadway Database person ID same as Wikidata", "Short description is different from Wikidata", "PMID", "ISBN", "doi"] 
degree = 1
path = []
path_found = False
current_generation = []

class Node:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.parent = None
        self.children = []
        self.searched = False

    def get_url(self):
        return self.url

    def check_searched(self):
        if self.searched == True:
            return True
        else:
            return False

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



"""
# Use ThreadPool to find current children 
    with ThreadPoolExecutor(max_workers=None) as executor:
        futures = [executor.submit(child_node.find_children) for child_node in current_node.children]
        results = []
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
"""

def attempt_match_children(current_node, to_node):
    global path_found
    global current_generation
    global path 

    current_node.find_children()

    # print(str(current_node.children))
    # Check children for any matches w/ to_node 
    for child_node in current_node.children:
        # Mark child_node as already searched
        child_node.searched = True
        # If child_node is the to_node, search is over
        if child_node.url == to_node.url:
            path.append(current_node)
            path.append(child_node)
            print("yaw")
            path_found = True
            return True
    return False

# Determine amount of degrees and commonalities, with origin and end being urls
def determine_path(from_node, to_node):
    global path_found
    global current_generation
    global path

    # 0th degree
    if from_node.url == to_node.url:
        path_found == True
        return path

    # 1st degree
    attempt_match_children(from_node, to_node)
    path.append(from_node)

    # 2+ degree: if none of the children match, continue to search through loop
    current_node = from_node
    current_generation = current_node.children
    temp_generation = []
    
    while path_found == False: 
        print("degree xd")
        # Keep Looping through each sibling_node and check sibling's children
        for sibling_node in current_generation:
            attempt_match_children(sibling_node, to_node)
            temp_generation.extend(sibling_node.children)
            # If found match in 2nd degree
            if path_found == True:
                return sibling_node
        # If none of the siblings in the level matched, move to higher degree
        if path_found == False:
            current_generation = temp_generation

    return path
    
    
    """# Check degree
    global degree
    global path

    path_found = False

    path.append(from_node)
    from_node.find_children()

    # Check if any child_node is the to_node
    if to_node in from_node.children:
        path.append(to_node)
        path_found = True
        return
         # If not, raise degree
    
    current_node = from_node
    while path_found == False:
        start = time.time()
        # Use ThreadPool to find all children data
        with ThreadPoolExecutor(max_workers=None) as executor:
            futures = [executor.submit(child_node.find_children) for child_node in current_node.children]
            results = []
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())
                number += 1
        # Check children for any matches w/ 
        for child_node in current_node.children:
            child_node.searched = True
            if child_node.url == to_node.url:
                path.append(child_node)
                path_found = True
                return
        print(time.time() - start)
    """


def main():
    global current_generation
    root = Node("Kevin Bacon", "https://en.wikipedia.org/wiki/Kevin_Bacon")
    current_generation.append(root)
    target = Node("Law of attraction (New Thought)", "https://en.wikipedia.org/wiki/Law_of_attraction_(New_Thought)")
    determine_path(root, target)
    for node in path:
        print(node.url)

if __name__ == '__main__':
    main()
