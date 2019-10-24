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
import matplotlib.pyplot as plt

def index(request):
    if request.method == 'POST':
        upload = DocumentForm(request.POST, request.FILES)
        if upload.is_valid():
            filename = request.FILES['docfile'].name
            with open('media/'+filename, 'wb+') as destination:
                for chunk in request.FILES['docfile'].chunks():
                    destination.write(chunk)
            fileType = upload.cleaned_data['inputFormat']
            return HttpResponseRedirect('/network/'+filename+"/"+fileType+"/")
    else:
        upload = DocumentForm()
    return render(request,"NetworkViewer/index.html",{'form':upload})

def network(request, n, f):
    fileType=f
    inputFile=n
    htmlFile = "./NetworkViewer/networks/"+n.split(".")[0]+".html"

    ngx=None
    if fileType=='geneSpider':
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=',', header=None)
        nxg = nx.from_numpy_matrix(np.array(networkDf),create_using=nx.MultiDiGraph())
    else:
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=' ', header=None)
        nxg = nx.from_pandas_edgelist(networkDf, source =0, target=1)

    #nxg = nx.complete_graph(5)
    #nxg = nx.generators.directed.random_k_out_graph(10, 3, 0.5)

    diameter = 0#nx.diameter(nxg, e=None)
    clusteringCoeffs = 0#nx.clustering(nxg)
    clusteringCoeff= 0#np.mean(list(clusteringCoeffs.values()))
    allCliques = None#nx.find_cliques(nxg)
    cliques =0#len(list(allCliques))

    pos = nx.spring_layout(nxg)
    nx.draw(nxg, pos)
    plt.savefig("./NetworkViewer/templates/NetworkViewer/networks/"+inputFile.split(".")[0]+".png", format="PNG")
    plt.clf()

    g = Network()
    g.barnes_hut(gravity=-2000,
        central_gravity=0.02,
        spring_length=1,
        spring_strength=0.000001,
        damping=0.09,
        overlap=0)

    g.toggle_physics(True)
    # g.show_buttons(filter_=['physics'])
    if nx.is_directed(nxg):
        g.directed=True

    g.from_nx(nxg)
    g.height="100%"
    g.width="100%"
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

def downloadNetworkAsPng(request):
    file_path = "./NetworkViewer/templates/NetworkViewer/networks/"
    fileName=file_path+request.POST['file'].split(".")[0]+".html"
    pngFileName = file_path+request.POST['file'].split(".")[0]+".png"

    if os.path.exists(pngFileName):
        with open(pngFileName, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(pngFileName)
            return response
    raise Http404
