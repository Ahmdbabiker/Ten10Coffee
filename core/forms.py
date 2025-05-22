from django import forms
from .models import Product

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ["name", "desc", "price", "image", "tag", "extras"]

        widgets = {
            'extras': forms.CheckboxSelectMultiple,
        }
