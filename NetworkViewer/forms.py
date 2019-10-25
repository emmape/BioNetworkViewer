from django import forms

inputFormats= [
    ('adjacencyList', 'Edge List'),
    ('directedAdjacencyList', 'Directed Edge List'),
    ('adjacencyMatrix', 'Adjacency Matrix, comma separated'),
    ('directedAdjacencyMatrix', 'Directed Adjacency Matrix, comma separated'),
    ('geneSpider', 'Gene Spider matrix'),
    ('funCoup', 'FunCoup Network')
    ]

class DocumentForm(forms.Form):
    docfile = forms.FileField(label='')
    inputFormat= forms.CharField(label='Specify your input format', widget=forms.Select(choices=inputFormats))
