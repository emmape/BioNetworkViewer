from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
import networkx as nx
import os
from pyvis.network import Network

# Create your views here.
def index(request):
    return render(request, 'NetworkViewer/index.html')

def network(request):

    inputFile="test.txt"
    # networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/test.txt'), sep=' ', header=None)
    # network = nx.from_pandas_edgelist(networkDf, source =0, target=1)
    # G = Network()
    nxg = nx.complete_graph(5)
    diameter = nx.diameter(nxg, e=None)
    clusteringCoeffs = nx.clustering(nxg)
    clusteringCoeff= np.mean(list(clusteringCoeffs.values()))
    allCliques = nx.find_cliques(nxg)
    cliques = len(list(allCliques))
    g = Network()

    g.barnes_hut()
    g.toggle_physics(True)
    # g.show_buttons(filter_=['physics'])
    g.from_nx(nxg)
    g.height="100%"
    g.width="100%"
    # g.add_nodes([1,2,3], value=[10, 100, 400], title=["I am node 1", "node 2 here", "and im node 3"], x=[21.4, 54.2, 11.2], y=[100.2, 23.54, 32.1], label=["NODE 1", "NODE 2", "NODE 3"], color=["#00ff1e", "#162347", "#dd4b39"])
    # G.from_nx(network)
    g.save_graph("./NetworkViewer/templates/NetworkViewer/networks/test.html")
    context={
        "diameter": diameter,
        "clustering": clusteringCoeff,
        "cliques": cliques,
        "inputFile": inputFile
    }
    return render(request, 'NetworkViewer/viewNetwork.html', context)
