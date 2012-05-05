from django.db import models
from django.forms import ModelForm
from models import *
from django import forms

class UserLoginForm(forms.Form):
    username=forms.CharField(help_text='Your username as registered with the ERP')
    password=forms.CharField(widget=forms.PasswordInput, help_text='Your password. If you do not remember this, please use the link below')
    
class forgot_password_form(ModelForm):
	
	class Meta:
		model=forgot_password
		exclude=('date','activation_key')
		
		
class Change_password (forms.Form):

    password = forms.CharField(min_length = 6,
                               max_length = 30,
                               widget = forms.PasswordInput)
    password_again = forms.CharField(min_length=6,max_length = 30,
                                     widget = forms.PasswordInput)

class ResetPasswordForm(forms.Form):
    password = forms.CharField(min_length = 6, max_length = 30, widget = forms.PasswordInput, help_text = 'Enter a password that you can remember')
    password_again = forms.CharField(max_length = 30, widget = forms.PasswordInput, help_text = 'Enter the same password that you entered above')
    
    def clean_password(self):
        if self.prefix:
            field_name1 = '%s-password'%self.prefix
            field_name2 = '%s-password_again'%self.prefix
        else:
            field_name1 = 'password'
            field_name2 = 'password_again'
            
        if self.data[field_name1] != '' and self.data[field_name1] != self.data[field_name2]:
            raise forms.ValidationError ("The entered passwords do not match.")
        else:
            return self.data[field_name1]
