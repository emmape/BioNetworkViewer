from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
import networkx as nx
import os
from pyvis.network import Network
from django.shortcuts import render
from .forms import DocumentForm
from django.http import HttpResponseRedirect


# Create your views here.
def index(request):
    # return render(request, 'NetworkViewer/index.html')
    if request.method == 'POST':
        upload = DocumentForm(request.POST, request.FILES)
        if upload.is_valid():
            filename = request.FILES['docfile'].name
            with open('media/'+filename, 'wb+') as destination:
                for chunk in request.FILES['docfile'].chunks():
                    destination.write(chunk)
            return HttpResponseRedirect('/network/'+filename+"/")
    else:
        upload = DocumentForm()
    return render(request,"NetworkViewer/index.html",{'form':upload})

def network(request, n):

    inputFile=n
    networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=' ', header=None)
    nxg = nx.from_pandas_edgelist(networkDf, source =0, target=1)
    # nxg = nx.complete_graph(5)
    diameter = 0#nx.diameter(nxg, e=None)
    clusteringCoeffs = 0 #nx.clustering(nxg)
    clusteringCoeff= 0#np.mean(list(clusteringCoeffs.values()))
    allCliques = None#nx.find_cliques(nxg)
    cliques =0# len(list(allCliques))
    g = Network()

    g.barnes_hut()
    g.toggle_physics(True)
    # g.show_buttons(filter_=['physics'])
    g.from_nx(nxg)
    g.height="100%"
    g.width="100%"
    # g.add_nodes([1,2,3], value=[10, 100, 400], title=["I am node 1", "node 2 here", "and im node 3"], x=[21.4, 54.2, 11.2], y=[100.2, 23.54, 32.1], label=["NODE 1", "NODE 2", "NODE 3"], color=["#00ff1e", "#162347", "#dd4b39"])
    # G.from_nx(network)
    g.save_graph("./NetworkViewer/templates/NetworkViewer/networks/"+inputFile+".html")
    context={
        "diameter": diameter,
        "clustering": clusteringCoeff,
        "cliques": cliques,
        "inputFile": inputFile
    }
    return render(request, 'NetworkViewer/viewNetwork.html', context)

def handle_uploaded_file(f):
    with open('/media/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
