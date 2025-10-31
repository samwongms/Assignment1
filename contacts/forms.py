from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['message']
        widgets = {
            'message' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' : '5',
                'placeholder' : 'Enter your message here...'
            }),
        }