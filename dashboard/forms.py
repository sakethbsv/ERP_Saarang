from django.db import models
from django.forms import ModelForm
from models import *
from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
    short_description=forms.CharField(max_length=100)
 
    def clean_title(self):
        given_title = self.cleaned_data['title']
        if given_title == '':
            raise forms.ValidationError ('Please enter your title.')
        return given_title

    class Admin:
        pass
    class Meta:
        widgets = {'title': forms.Textarea(attrs={'cols': 80, 'rows': 20}),}

   

class shout_box_form(forms.Form):
    comments=forms.CharField(max_length=200)

""""

class change_pic(forms.Form):
    file  = forms.FileField()


"""
