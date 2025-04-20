from django import forms
from quote.models import QuoteModel

class QuoteForm(forms.ModelForm):
    class Meta:
        model = QuoteModel
        fields = ['quote', 'text', 'author']