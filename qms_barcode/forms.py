from django import forms
from django.forms import ModelForm
from django.db import models as d_models
import re 
from django.template import Template, Context
from django.utils.safestring import mark_safe
from erp_test.qms_barcode import models
from erp_test.misc import util
from erp_test import settings

EVENT_LIST=(
	('Hackfest' ,'Hackfest'),
	('Robotics' , 'Robotics'),
	('Contraption' , 'Contraption'),
	('Puzzle' ,'Puzzle'),
	)


COLLEGE_CHOICES = [(e.id, "%s, %s, %s"%(e.state,e.city,e.name)) for e in models.College.objects.order_by("state","city","name",)]
alnum_re = re.compile(r'^[\w.-]+$') # regexp. from jamesodo in #django  [a-zA-Z0-9_.]
alphanumric = re.compile(r"[a-zA-Z0-9]+$")


class AddParticipantForm(ModelForm):
    college        = forms.CharField  (max_length=120,
                                       widget=forms.TextInput(attrs={'id':'coll_input'}),
                                       help_text='Select your college from the list. If it is not there, use the link below')
                                       
#    username = forms.CharField(widget=forms.TextInput(attrs={'':'b'}))

#    username = db.StringProperty(verbose_name='b')

    class Meta:
        model = models.Participant
        fields=('username','first_name','mobile','college','gender','email','branch','degree','year')
	widgets = {'username': forms.TextInput(attrs={'name': "Gen"}),  }
#        exclude=('last_name','password','is_staf)

    def clean_college(self):
        coll_input = self.cleaned_data['college']
        try:
            print "Came in the form function"
            coll_name, coll_city = coll_input.rsplit(',',1)
            print coll_name
            print coll_city
            collchk = models.College.objects.get(name = coll_name, city=coll_city)
            print collchk.id
        except: 
            raise forms.ValidationError ("Invalid college name, or college does not exist")
        return collchk
        
    # The mobile number must be ten digits only else raise an error
    def clean_mobile(self):
        mobile_input = self.cleaned_data['mobile']
        if len(mobile_input) != 10: 
            print "The mobile number has error"
            raise forms.ValidationError("The Mobile number must have ten digits .It has " + str(len(mobile_input)) +" digits now")
        else:
            parti = models.Participant.objects.filter(mobile=mobile_input)
            if parti:
	        raise forms.ValidationError("This Mobile already exists")
                        
        return self.cleaned_data['mobile']
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if  username.isdigit() and (len(username)!=5) :
            raise forms.ValidationError("The barcode doest have five digits")
        elif len(username)!=8 and not username.isdigit():
            raise forms.ValidationError("The rollnumber is not right")
        else :
            return username
        
        
               
class SearchForm(forms.Form):

    name = forms.CharField(max_length = 50,required=False)
    barcode = forms.CharField(max_length=50,required=False)
    mobile = forms.CharField(max_length=50,required=False)
 
    class Admin:
        pass

	def clean(self):
		name=self.cleaned_data['name']
		barcode=self.cleaned_data['barcode']
		mobile=self.cleaned_data['mobile']
		if name == '' and barcode == '' and mobile == '':
			
			raise forms.ValidationError("Please Enter atleast One Value")
		return self
		
class BarcodeLogin(forms.Form):
    username=forms.CharField(help_text='Your username as registered with the ERP')
    password=forms.CharField(widget=forms.PasswordInput, help_text='Your password. If you do not remember this, please use the link below')

class LoginRegisterForm(forms.Form):
    barcode = forms.CharField(max_length = 10)
    
class EditUserForm(ModelForm):
            
    class Meta:
        model = models.Participant
        fields=('username','first_name','last_name','gender','email','branch','degree','year')
        #exclude=('barcode', 'college','registered')

class BarcodeRegisterForm(forms.Form):    
    barcode = forms.CharField(max_length=50, label='Barcode/Roll Number') 
    class Admin:
        pass
    
    def clean_barcode(self):
        cd = self.cleaned_data['barcode']
        if len(cd) == 8:
	    try:
	        parti = models.Participant.objects.get(username=cd)
	    except models.Participant.DoesNotExist:
	        college = models.College.objects.get(id=1)
	        parti = models.Participant(username=cd, password="shaastra", email="%s@smail.iitm.ac.in"%cd, college=college, mobile='9090909090')
		parti.save()
	try:
	    u = models.User.objects.get(username=cd)
        except models.User.DoesNotExist:
           raise forms.ValidationError("This Username does not exist")
	return cd
               
class EventEditForm(forms.ModelForm):
    class Meta:
	model = models.Event
	fields = ('cap_team','cap_team_min','cap_iitm','cap_non_iitm','cap_iitm_waiting','cap_non_iitm_waiting')
    #    include = ('')        


class ShaastraIDForm(forms.Form):
    shaastra_id = forms.CharField()
    
    class Admin:
        pass

class OnlineRegForm(forms.Form):
    username = forms.CharField()
    
    class Admin:
        pass

class AddCollegeForm (ModelForm):
    class Meta:
        model = models.College
        fields=('name','city','state')

#class AddWinnerForm(forms.Modelform):

#	college        = forms.CharField  (max_length=120,
 #                                      widget=forms.TextInput(attrs={'id':'coll_input'}),
  #                                     help_text='Select your college from the list. If it is not there, use the link below')
	#college        = forms.CharField  (max_length=120,
     #                                  widget=forms.TextInput(attrs={'id':'coll_input'}),
      #                                 help_text='Select your college from the list. If it is not there, use the link below')


