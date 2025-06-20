from django import forms
from .models import Product, City, MaintenanceMode

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ["name", "desc", "price", "image", "tag", "extras"]

        widgets = {
            'extras': forms.CheckboxSelectMultiple,
        }


class CityForm(forms.ModelForm):

    class Meta:
        model = City
        fields = ["name", "shipping_price"]


class MaintenanceModeForm(forms.ModelForm):

    class Meta:
        model = MaintenanceMode
        fields = ["on"]
