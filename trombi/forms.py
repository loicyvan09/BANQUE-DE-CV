from django import forms

class EmailCVForm(forms.Form):
    email_destinataire = forms.EmailField(
        label="Email du destinataire", 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'email du destinataire'})
    )
    sujet = forms.CharField(
        label="Sujet", 
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le sujet'})
    )
    message = forms.CharField(
        label="Message", 
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Entrez votre message', 'rows': 5})
    )
