from django.db import models
from django.contrib import admin
from django.conf import settings
from users.models import College , Group
from django.contrib.auth.models import User
# Create your models here.
#import rss

GENDER_CHOICES = (
    ('M','Male'),
    ('F','Female'),
)

YEAR_CHOICES = (
    ('0','0'),	# This is for School Childrens
    ('1','1'), 
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'), 	# This is for professors
)

DEGREE_CHOICES = (
    ('BT','B.Tech'),
    ('MT','M.Tech'),
    ('BS','B.Sc'),
    ('MS','M.Sc'),
    ('BA','B.A.'),
    ('MA','M.A.'),
    ('PH','PHD'),
    ('BP','B.Pharm'),
    ('MP','M.Pharm'),
)

DEPARTMENT_CHOICES = (
    ('AR','Arts'),
    ('AC','Accounting'),
    ('AM','Applied Mechanics / Mechatronics'),
    ('AE','Aerospace Engineering'),
    ('AU','Automobile Engineering'),
    ('BM','Biotech / Biochemical / Biomedical'),
    ('BI','Biology'),
    ('CE','Ceramic Engineering'),
    ('CH','Chemical Engineering'),
    ('CY','Chemistry'),
    ('DE','Design / Engineering Design'),
    ('CE','Civil Engineering'),
    ('CS','Computer Science and Engineering'),
    ('EC','Electronics and Communications Engineering'),
    ('EA','Electrical and Electronics Engineering'),
    ('EE','Electrical Engineering'),
    ('EI','Electronics and Instrumentation Engineering'),
    ('EP','Engineering Physics'),
    ('ES','Economics'),
    ('FT','Fashion Technology'),
    ('HS','Humanities and Social Sciences'),
    ('IP','Industrial Production    / Production'),
    ('IT','Information Technology and Information Science(IT/IS)'),
    ('MG','Management'),
    ('MN','Manufacturing'),
    ('MA','Mathematics'),
    ('MM','Metallurgy and Material Science'),
    ('ME','Mechanical Engineering'),
    ('OC','Ocean Engineering and Naval Architecture'),
    ('OT','Others'),
    ('PH','Physics'),
    ('TC','Telecom'),
    ('TE','Textile Engineering'),
)
STATE_CHOICES = (
	("Andhra Pradesh" , "Andhra Pradesh"),
	("Arunachal Pradesh" , "Arunachal Pradesh"),
	("Assam" , "Assam"),
	("Bihar" , "Bihar"),
	("Chhattisgarh" , "Chhattisgarh"),
	("Goa" , "Goa"),
	("Gujarat" , "Gujarat"),
	("Haryana" , "Haryana"),
	("Himachal Pradesh" , "Himachal Pradesh"),
	("Jammu And Kashmir" , "Jammu And Kashmir"),
	("Jharkhand" , "Jharkhand"),
	("Karnataka" , "Karnataka"),
	("Kerala" , "Kerala"),
	("Madhya Pradesh" , "Madhya Pradesh"),
	("Maharashtra" , "Maharashtra"),
	("Manipur" , "Manipur"),
	("Meghalaya" , "Meghalaya"),
	("Mizoram" , "Mizoram"),
	("Nagaland" , "Nagaland"),
	("Orissa" , "Orissa"),
	("Punjab" , "Punjab"),
	("Rajasthan" , "Rajasthan"),
	("Sikkim" , "Sikkim"),
	("Tamil Nadu" , "Tamil Nadu"),
	("Tripura" , "Tripura"),
	("Uttar Pradesh" , "Uttar Pradesh"),
	("Uttarakhand" , "Uttarakhand"),
	("West Bengal" , "West Bengal"),
	("Andaman And Nicobar Islands" , "Andaman And Nicobar Islands"),
	("Chandigarh" , "Chandigarh"),
	("Dadra And Nagar Haveli" , "Dadra And Nagar Haveli"),
	("Daman And Diu" , "Daman And Diu"),
	("Lakshadweep" , "Lakshadweep"),
	("NCT/Delhi" , "NCT/Delhi"),
	("Puducherry" , "Puducherry"),
	("Outside India" , "Outside India"),
)
"""
EVENT_LIST=(
	('Hackfest' ,'Hackfest'),
	('Robotics' , 'Robotics'),
	('Contraption' , 'Contraption'),
	('Puzzle' ,'Puzzle'),
	('Online' ,'Online'),
	('Aerofest' ,'Aerofest'),		
	)
"""
PLACE_LIST=(
	('1','1'),
	('2','2'),
	('3','3'),
	('4','4'),
	('5','5'),
	('6','6'),
	('7','7'),
	('8','8'),
	('9','9'),
	('10','10'),
)
class Event(Group):
    
    cap_team_min = models.IntegerField (default = 1 , help_text = 'Minimum no. of members in a team' ) 
    cap_team= models.IntegerField (default = 3 , help_text = 'Maximum no. of members in a team')
    cap_iitm= models.IntegerField (default = 100 , help_text='Max no. of teams iitm teams' )
    cap_non_iitm= models.IntegerField (default = 100 , help_text='Max no. of teams non-iitm teams')
    cap_iitm_waiting= models.IntegerField (default = 50 , help_text='Max no of iitm waiting teams')
    cap_non_iitm_waiting= models.IntegerField (default = 50 , help_text='Min no of iitm waiting teams')
    count_team = models.IntegerField(default =0)
    count_team_iitm = models.IntegerField(default =0) 
    
    def __unicode__(self):
	return "%s" %(self.name)    
	

class Participant(User):
    """
		The pasword is kept has "shaastra"
    """
    gender = models.CharField(max_length=1, choices = GENDER_CHOICES, default='M')
    mobile = models.CharField(max_length=10 )
    college = models.ForeignKey(College)
    branch = models.CharField(max_length=75, choices = DEPARTMENT_CHOICES, default='Chemical Engineering', blank=True)
    degree = models.CharField(max_length=8, choices = DEGREE_CHOICES, default='B.Tech', blank=True)
    year =  models.CharField(max_length=8, choices = YEAR_CHOICES, default='2', blank=True)
    class Admin:
        pass
    def __unicode__(self):
        return "%s"%(self.username)	
        	
    def save(self , *args ,**kwargs):
    	if not self.password :
    	    self.password = "Shaastra"

    	super(Participant,self).save(*args ,**kwargs)
    	co
    	
    def __str__(self):
        return self.username


class Winners(models.Model):
	event=models.ForeignKey(Event)
	winner=models.ManyToManyField(Participant)
	is_place=models.IntegerField(choices = PLACE_LIST)
	class Admin:
		pass

