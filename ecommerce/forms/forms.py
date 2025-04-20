
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'availability', 'description', 'image_url', 'image_local']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
