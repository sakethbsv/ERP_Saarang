from django.db import models
from django.contrib.auth.models import User
from erp_test import settings
# from erp_test.department.models import Department
from erp_test.users.models import Group
from erp_test.misc.helper import is_core, is_coord, get_page_owner, get_file_path
import os

STAT_CHOICES= (
	('A','Accepted'),
	('R','Rejected'),
	('V','Revised'),
	('P','Pending'),
)

STAT_CHOICES2= (
	('A','Accepted'),
	('R','Rejected'),
	('V','Available'),
)

DEFAULT_STATUS = 'P'
DEFAULT_STATUS2 = 'V'
class AbstractBudget(models.Model):

    particular    = models.CharField(max_length=200 , null=True)
    requirement_date   = models.DateField(null=True , blank=True)
    requester       = models.ForeignKey(User, related_name = '%(app_label)s_%(class)s_creator', null=True)
    amount_a       = models.BigIntegerField (null=True)
    amount_b       = models.BigIntegerField(null=True)
    amount_revised = models.BigIntegerField(null=True)
    status        = models.CharField(max_length=1,choices=STAT_CHOICES,default = DEFAULT_STATUS)
    
    class Meta:
        abstract = True

class Budget_Department(AbstractBudget):
    department = models.ForeignKey(Group, related_name = '%(app_label)s_%(class)s_creator', null=True)        
    # department = models.ForeignKey(Department, related_name = '%(app_label)s_%(class)s_creator', null=True)        

class Budget_Event(AbstractBudget):
    event = models.ForeignKey(Group, related_name = '%(app_label)s_%(class)s_creator', null=True)       
    # department = models.ForeignKey(Event, related_name = '%(app_label)s_%(class)s_creator', null=True)       

class Advance_Payment(models.Model):
    amount_request = models.BigIntegerField(null=True)
    link = models.ForeignKey(Budget_Event, null=True)
    finance_approval = models.BooleanField()
    events_approval = models.BooleanField()
    time_stamp = models.DateTimeField (auto_now = True, editable = False)    
    status        = models.CharField(max_length=1,choices=STAT_CHOICES2,default = DEFAULT_STATUS2)    
    
class Buffer(models.Model):
    reason = models.CharField(max_length=200 , null=True)
    amount_request = models.BigIntegerField(null=True)
    finance_approval = models.BooleanField()
    events_approval = models.BooleanField()
    event = models.ForeignKey(Group, related_name = '%(app_label)s_%(class)s_creator', null=True)       

