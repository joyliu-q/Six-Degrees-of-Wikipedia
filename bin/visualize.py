# Imports
import networkx as nx
import matplotlib.pyplot as plt

# Local Imports
from main import Node 

G = nx.Graph()
G.add_edge(1,2)
G.add_edge(1,3)
nx.draw(G, with_labels=True)
plt.show()

