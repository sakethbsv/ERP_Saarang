from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings
# Create your models here.

GENDER_CHOICES = (
    ('M','Male'),
    ('F','Female'),
)

DEP_CHOICES = (
	("Events", "Events"),
	("QMS", "Quality Management"),
	("Finance", "Finance"),
	("Sponsorship", "Sponsorship"),
	("Evolve", "Evolve"),
	("Facilities", "Facilities"),
	("Webops", "Web Operations"),
	("Hospitality", "Hospitality"),
	("Publicity", "Publicity"),
	("Design", "Design"),
)


HOSTEL_CHOICES  =(
        ("Ganga", "Ganga"),
        ("Mandak", "Mandak"),
        ("Jamuna", "Jamuna"),
        ("Alak", "Alak"),
        ("Saraswati", "Saraswati"),
        ("Narmada", "Narmada"),
        ("Godav", "Godav"),
        ("Pampa", "Pampa"),
        ("Tambi", "Tambi"),
        ("Sindhu", "Sindhu"),
        ("Mahanadi", "Mahanadi"),
        ("Sharavati", "Sharavati"),
        ("Krishna", "Krishna"),
        ("Cauvery", "Cauvery"),
        ("Tapti", "Tapti"),
        ("Bhramhaputra", "Bhramhaputra"),
        ("Sarayu", "Sarayu"),
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

class userprofile(models.Model):
    """
    User's profile which contains all personal data.
    """
    user = models.ForeignKey(User, unique=True)
    nickname = models.CharField(max_length=30, blank=True)
    name = models.CharField(max_length=30, blank=True)
    chennai_number = models.CharField(max_length=15, blank=True)
    summer_number = models.CharField(max_length=15, blank=True)
    summer_stay = models.CharField(max_length=30, blank=True)
    hostel = models.CharField(max_length=15, choices = HOSTEL_CHOICES, blank=True)
    room_no = models.IntegerField(default = 0, blank=True)

    class Meta:
        pass
    def __str__(self):
        return '%s %s' %(self.user.username, self.nickname)

    def get_dept (self):
        """
        Return Department that user belongs to, if it exists.
        Else, return None.
        """
        return self.user.group_set.filter (label__name = 'Department')[0]

    class Admin:
        pass

class Materials(models.Model):
    # name of the  person who asked or gave
    user = models.ForeignKey(User, unique=True, related_name="item_borrower")
    # the material which has been asked for
    item = models.CharField(max_length=50)
    # no. of items borrowed
    item_no = models.IntegerField(default=1)
    # time of borrow
    borrowed_time = models.DateTimeField(null=True ,blank=True)
    # time of return
    return_time = models.DateTimeField(null=True ,blank=True)
    # if the person got/given the item this will be true
    item_got = models.BooleanField(default=False)
    # if the person returns/takes the item this will be true
    item_returned = models.BooleanField(default=False)
    # name of the person/hostel/deptartment borrowed/lent from
    user_2 = models.ForeignKey(User , unique=True, related_name="item_lender")

    def __str__(self):
        return self.item

    class Admin:
        pass

class invitation(models.Model):
    core = models.ForeignKey(User , related_name="the core who has invited the user")
    invitee = models.CharField(max_length=50)#name of the coord
    roll_no = models.CharField(max_length=8)
    email_id = models.EmailField()
    time = models.DateField()

    class Admin:
	pass


class userphoto(models.Model):
    name=models.ForeignKey(User)
    photo_path=models.FileField(upload_to=settings.MEDIA_ROOT ,default="/upload_files/ee10b000/PROFILE_PIC_OF_THE_USER")

class Circle(models.Model):
    user=models.ForeignKey(User)
    circle_name=models.CharField(max_length="50")
    circle_photo=models.ManyToManyField(userphoto ,blank=True)
    
    def __str__(self):
	return str(self.photo_path)
    class Admin:
	pass

# class EventDivision (models.Model):
#     """
#     Division of Events Dept. eg. Coding, Aero, etc.
#     """
#     name = models.CharField(max_length=100 , null=True)    

#     def __str__(self):
#         return self.name
        
# class Event(models.Model):
#     """
#     As of now, Super-Coords are assigned to every event which they
#     cover. This saves us the hassle of creating a special model with a
#     fk to EventDivision.
#     """

#     name = models.CharField(max_length=100 , null=True)    
#     division = models.ForeignKey (EventDivision, blank = True)
#     coords  = models.ManyToManyField (User, blank = True)

#     class Admin:
# 	pass
#     def __str__(self):
#         return self.name

class Label(models.Model):
    """
    Label for a Group, eg. 'Department', 'Event', etc.
    I think we'll use this for everything else that needs a label as
    well.
    """
    name = models.CharField (max_length = 100 , blank = True)

    def __str__ (self):
        return self.name
        
class Group(models.Model):
    """
    Store information about a group and its members and link to its parent in the hierarchy of groups.
    """
    label = models.ForeignKey (Label)
    name = models.CharField (max_length = 100)
    parent = models.ForeignKey ('self', null = True, blank = True, related_name = 'children_set')
    members = models.ManyToManyField (User, blank = True)
    timestamp		=models.DateTimeField(auto_now = True , editable = False)
    def __str__(self):
        return self.name


class College(models.Model):
    name=models.CharField (max_length = 255,help_text  = 'The name of your college. Please refrain from using short forms.')
    city=models.CharField (max_length = 30,help_text  = 'The name of the city where your college is located. Please refrain from using short forms.' )
    state=models.CharField (max_length = 40,choices    = STATE_CHOICES,help_text  = 'The state where your college is located. Select from the drop down list' )

    def __unicode__(self):
        return "%s, %s, %s"%(self.name, self.city, self.state)

    class Admin:
        pass
