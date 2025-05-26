from django import forms
from core.models import Profile


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].required = True
        self.fields['city'].required = True

    class Meta:
        model = Profile
        fields = ["phone_number", "city", "address", "home_location"]
