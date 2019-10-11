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
import csv
from django.urls import resolve
from django.utils.encoding import smart_str
import matplotlib.pyplot as plt


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
    htmlFile = "./NetworkViewer/networks/"+n.split(".")[0]+".html"
    inputFile=n
    # inputFile="test.txt"
    networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=' ', header=None)
    nxg = nx.from_pandas_edgelist(networkDf, source =0, target=1)
    # nxg = nx.complete_graph(5)
    diameter = 0#nx.diameter(nxg, e=None)
    clusteringCoeffs = 0 #nx.clustering(nxg)
    clusteringCoeff= 0#np.mean(list(clusteringCoeffs.values()))
    allCliques = None#nx.find_cliques(nxg)
    cliques =0# len(list(allCliques))
    pos = nx.spring_layout(nxg)
    nx.draw(nxg, pos)
    plt.savefig("./NetworkViewer/templates/NetworkViewer/networks/"+inputFile.split(".")[0]+".png", format="PNG")

    g = Network()
    g.barnes_hut()
    g.toggle_physics(True)
    # g.show_buttons(filter_=['physics'])
    g.from_nx(nxg)
    g.height="100%"
    g.width="100%"
    # g.add_nodes([1,2,3], value=[10, 100, 400], title=["I am node 1", "node 2 here", "and im node 3"], x=[21.4, 54.2, 11.2], y=[100.2, 23.54, 32.1], label=["NODE 1", "NODE 2", "NODE 3"], color=["#00ff1e", "#162347", "#dd4b39"])
    # G.from_nx(network)
    g.save_graph("./NetworkViewer/templates/NetworkViewer/networks/"+inputFile.split(".")[0]+".html")
    context={
        "diameter": diameter,
        "clustering": clusteringCoeff,
        "cliques": cliques,
        "inputFile": inputFile,
        "htmlFile": htmlFile
    }
    return render(request, 'NetworkViewer/viewNetwork.html', context)

def handle_uploaded_file(f):
    with open('/media/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def downloadNetwork(request):
    fileName=request.POST['file'].split(".")[0]+".html"
    file_path = "./NetworkViewer/templates/NetworkViewer/networks/"+fileName
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def downloadNetworkAsJpg(request):
    file_path = "./NetworkViewer/templates/NetworkViewer/networks/"
    fileName=file_path+request.POST['file'].split(".")[0]+".html"
    jpgFileName = file_path+request.POST['file'].split(".")[0]+".png"

    if os.path.exists(jpgFileName):
        with open(jpgFileName, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(jpgFileName)
            return response
    raise Http404
