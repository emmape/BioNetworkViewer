from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
import networkx as nx
import os
from pyvis.network import Network
from .forms import DocumentForm
from django.http import HttpResponseRedirect
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

    # The network parameters to be displayed are initiated. All parameters can not be calculated for all types of networks
    diameter = 0
    clusteringCoeff= 0
    cliques = 0
    degree = 0
    connectedComponents = 0
    stronglyConnectedomponents=0

    # Different file types needs to be handeled in different ways
    ngx=None
    if fileType=='geneSpider':
        # Gene spider matrix is read as a matrix that is then transposed, in order to get the directions right
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=',', header=None)
        networkDfTransposed = networkDf.T
        nxg = nx.from_numpy_matrix(np.array(networkDfTransposed),create_using=nx.MultiDiGraph())
    elif fileType == 'adjacencyList':
        # Adjacency lists/Edge lists are red as undirected pandas edgelists
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep='\s+', header=None)
        nxg = nx.from_pandas_edgelist(networkDf, source =0, target=1)
    elif fileType == 'directedAdjacencyList':
        # Directed edge lists need to be read as directed pandas edgelists
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep='\s+', header=None)
        nxg = nx.from_pandas_edgelist(networkDf, source =0, target=1, create_using=nx.MultiDiGraph())
    elif fileType == 'adjacencyMatrix':
        # Adjacency matrix need to be read as an undirected matrix
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=',', header=None)
        nxg = nx.from_numpy_matrix(np.array(networkDf))
    elif fileType == 'directedAdjacencyMatrix':
        # Directed Adjacency matrix need to be read as a directed matrix
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep=',', header=None)
        nxg = nx.from_numpy_matrix(np.array(networkDf),create_using=nx.MultiDiGraph())
    elif fileType == 'funCoup':
        # FunCoup-network-files contains several columns defining the evidence types and scores. Here, they are red as edge lists, only taking the genes and their edges into account
        networkDf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/'+inputFile), sep='\t')
        networkDfGenes = networkDf[['2:Gene1', '3:Gene2']]
        nxg = nx.from_pandas_edgelist(networkDfGenes, source ='2:Gene1', target='3:Gene2')

    # The networkx-networks are drawn as png-images, since the pyvis can not handle other formats than html.
    pos = nx.spring_layout(nxg)
    nx.draw(nxg, pos, with_labels = True)
    # nx.draw_networkx_edge_labels(nxg, pos, with_labels = True)
    plt.savefig("./NetworkViewer/templates/NetworkViewer/networks/"+inputFile.split(".")[0]+".png", format="PNG")
    plt.clf()

    # Initiating pyvis interactive network with customized graphics
    g = Network()
    g.barnes_hut(gravity=-2000,
        central_gravity=0.02,
        spring_length=1,
        spring_strength=0.000001,
        damping=0.09,
        overlap=0)
    g.toggle_physics(True)

    # Calculating network prooperties from the networkx graphs
    if nx.is_directed(nxg):
        g.directed=True
        stronglyConnectedomponents = nx.number_strongly_connected_components(nxg)
    else:
        connectedComponents = nx.number_connected_components(nxg)
        if connectedComponents ==1:
            diameter = nx.diameter(nxg, e=None)
        clusteringCoeffs =nx.clustering(nxg)
        clusteringCoeff= np.mean(list(clusteringCoeffs.values()))
        allCliques = nx.find_cliques(nxg)
        cliques =len(list(allCliques))
    degrees =nxg.degree()
    degreesOnly=[]
    for node, degree in degrees:
        degreesOnly.append(degree)
    degree= np.mean(degreesOnly)
    maxDegree=np.max(degreesOnly)

    # Filling the pyvis graph with nodes and edges from the networkx graph.
    allNodes = list(nxg.nodes)
    allSizes=[]
    # The nodes gets sizes according to their degree
    for d in degreesOnly:
        allSizes.append(40*(d/maxDegree))
    g.add_nodes(allNodes, size=allSizes)
    # The edges gets width according to their weights
    allEdges=nxg.edges(data=True)
    edges=[]
    for a, b, w in allEdges:
        edges.append((a, b, w.get('weight')))
    g.add_edges(edges)
    g.height="100%"
    g.width="100%"
    # The pyvis graph is saved as an html file, that is embedded in the network viewer-vindow
    g.save_graph("./NetworkViewer/templates/NetworkViewer/networks/"+inputFile.split(".")[0]+".html")

    # Exporting network properties to the html-view
    context={
        "diameter": ("%.2f" % diameter),
        "clustering": ("%.2f" % clusteringCoeff),
        "cliques": ("%.2f" % cliques),
        "degree":  ("%.2f" % degree),
        "connectedComponents": connectedComponents,
        "stronglyConnectedomponents": stronglyConnectedomponents,
        "inputFile": inputFile,
        "htmlFile": htmlFile
    }
    return render(request, 'NetworkViewer/viewNetwork.html', context)



# Function to store the uploaded file
def handle_uploaded_file(f):
    with open('/media/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



# Function to download the network as an html file
def downloadNetwork(request):
    fileName=request.POST['file'].split(".")[0]+".html"
    file_path = "./NetworkViewer/templates/NetworkViewer/networks/"+fileName
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404



# Function to download the network as a png file
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



# Customized error handler. Called if eg. the user tries to upload a network with an inappropriate file format
def customError(request):
    return render(request, 'NetworkViewer/500.html')
