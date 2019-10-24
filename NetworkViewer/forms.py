from django import forms

inputFormats= [
    ('other', 'Other'),
    ('geneSpider', 'GeneSpider')
    ]

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label=''
    )
    inputFormat= forms.CharField(label='Specify your input format', widget=forms.Select(choices=inputFormats))
