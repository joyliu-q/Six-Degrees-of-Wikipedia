# Import
from bs4 import BeautifulSoup, SoupStrainer
import numpy as np
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import time 
import sys
import concurrent
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future, as_completed, wait
import argparse
import string

# Viualization Imports
import networkx as nx
import matplotlib.pyplot as plt

# Argparse Set-up
parser = argparse.ArgumentParser(description="Find the Distance between Two Wikipedia Pages")
parser.add_argument('--fromtitle', type=str, required=True,
	help="the root wikipedia title")
parser.add_argument('--totitle', type=str, required=True,
	help="the target wikipedia title")
"""
parser.add_argument('--fromlink', type=str, required=True,
	help="the root wikipedia link")
parser.add_argument('--tolink', type=str, required=True,
	help="the target wikipedia link")
"""
parser.add_argument('--tp', action='store_true',
	help="enable threadpool (recommended for high depth)")
parser.add_argument('--graph', action='store_true',
	help="enable network graph creation")
parser.add_argument('--saveGraph', type=str,
	metavar='<path>', help='path to save graph network')
args = parser.parse_args()
if args.saveGraph and not args.graph:
    print("You must have --graph enabled to save the graph!")
    sys.exit(1)

# Tree Visualization
G = nx.DiGraph()

# Changable Variables
USE_THREADPOOL = False
if args.tp:
    USE_THREADPOOL = True
MAKE_GRAPH = False
if args.graph:
    MAKE_GRAPH = True

# Dismissed links are links shared by all sites and do not factor into 6 degrees of separation
dismissed_links = ["Talk", "Categories", "Contributions", "Article", "Read", "Main page", "Contents", "Current events", "Random article", "About Wikipedia", "Help", "Community portal", "Recent changes", "Upload file", "What links here", "Related changes", "Upload file", "Special pages", "About Wikipedia", "Disclaimers", "Articles with short description", "Short description matches Wikidata", "Wikipedia indefinitely semi-protected biographies of living people", "Use mdy dates from October 2016", "Articles with hCards", "BLP articles lacking sources from October 2017", "All BLP articles lacking sources", "Commons category link from Wikidata", "Articles with IBDb links", "Internet Off-Broadway Database person ID same as Wikidata", "Short description is different from Wikidata", "PMID", "ISBN", "doi"] 
degree = 0
path = []
path_found = False
current_generation = []
child_generation = []

# Configure args.fromtitle and args.totitle
args.fromtitle = string.capwords(args.fromtitle.lower()).replace(" ", "_")
args.totitle = string.capwords(args.totitle.lower()).replace(" ", "_")

# BS4 optimization
only_a_tags = SoupStrainer("a", href=lambda href: href and href.startswith('/wiki/'))

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
        global USE_THREADPOOL

        response = urlopen(self.url)
        soup = BeautifulSoup(response, 'html.parser', parse_only = only_a_tags)
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
                    # Visualization
                    self.children.append(child_node)

def attempt_match_children(current_node, to_node):
    global child_generation
    global path 
    global path_found
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
            # Special Threadpool to find children: attempt to stop bottleneck
            if USE_THREADPOOL == True:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    [executor.map(sibling_node.find_children()) for sibling_node in current_generation]
            # Keep Looping through each sibling_node and check sibling's children
            for sibling_node in current_generation:
                if sibling_node.searched == False:
                    attempt_match_children(sibling_node, to_node)
                    # If found match in current degree
                    if path_found == True:
                        return sibling_node
            # If none of the siblings in the level matched, move to higher degree
            if path_found == False:
                current_generation = child_generation
                child_generation = []
    return path


def main():
    global current_generation
    start = time.time()

    #root = Node("Kevin Bacon", "https://en.wikipedia.org/wiki/Kevin_Bacon")
    #target = Node("Neo-noir", "https://en.wikipedia.org/wiki/Hollywood")

    # Find/Check Valid Root and Target URL
    try: 
        urlopen("https://en.wikipedia.org/wiki/" + args.fromtitle)
        print("https://en.wikipedia.org/wiki/" + args.fromtitle)
        print("https://en.wikipedia.org/wiki/" + args.totitle)
        urlopen("https://en.wikipedia.org/wiki/" + args.totitle)
    except HTTPError:
        print("HTTPError: Invalid Name")
        sys.exit(1)
    except URLError:
        print("URLError: Invalid Name")
        sys.exit(1)
    except ValueError:
        print("ValueError: Invalid Name")
        sys.exit(1)

    root = Node("From Link", "https://en.wikipedia.org/wiki/" + args.fromtitle)
    target = Node("To Link", "https://en.wikipedia.org/wiki/" + args.totitle)
    
    current_generation.append(root)
    determine_path(root, target)
    
    # Present Data
    path_names = []
    for node in path:
        path_names.append(node.title)
    print(time.time() - start)
    print("Path: " + str(path_names))
    print("Degree: " + str(degree))

    # Visualization of Path
    if MAKE_GRAPH:
        for i, node in enumerate(path):
            G.add_node(node.title)
            if i > 0:
                G.add_edge(path[i-1].title, node.title)
            print(node.url)
        nx.draw(G, with_labels=True)
        if args.saveGraph:
            plt.savefig(args.saveGraph)
            #plt.savefig('../res/found_path.svg')
        else:
            plt.show()

if __name__ == '__main__':
    main()
