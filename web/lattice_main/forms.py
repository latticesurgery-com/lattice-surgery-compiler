from django import forms
from .models import Contact

class Contact_Form(forms.ModelForm):
    name = forms.CharField(label="Name",max_length=30)
    email = forms.EmailField(label="Email")
    subject = forms.CharField(label='Subject',max_length=100)
    message = forms.CharField(label='Message',max_length=300,widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ['name','email','subject','message']
