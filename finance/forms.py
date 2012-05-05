from django.db import models
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from models import *
from django import forms

    

class BudgetForm (ModelForm):
    class Meta:
        model = Budget_Department
        exclude = ('requester', 'status','amount_revised','requester_event','department')
class BudgetFormEvent (ModelForm):
    class Meta:
        model = Budget_Event
        exclude = ('requester', 'status','amount_revised','requester_event','department')
        
class BudgetFormCoord (ModelForm):
    class Meta:
        model = Budget_Department
        exclude = ('requester','department')

class BudgetFormCoordEvent (ModelForm):
    class Meta:
        model = Budget_Event
        exclude = ('requester','department')
class AdvancePortalForm (forms.Form):
    amount_request = forms.IntegerField(required=False)    

class BufferForm (ModelForm):
    class Meta:
        model = Buffer
        exclude = ('department','status', 'events_approval', 'finance_approval')
class BoolForm (forms.Form):
    bool_val = forms.BooleanField()
