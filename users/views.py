# Create your views here.
from django.shortcuts import render_to_response, redirect
# from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template.context import Context, RequestContext
from forms import * 
from django import forms
from erp_test.users.models import *
from erp_test.misc.util import *
from erp_test.misc.helper import *
from erp_test.dashboard.forms import *			
from django.contrib import auth
import sha,random,datetime
from erp_test.users.forms import *
from django.core.mail import send_mail,EmailMessage,SMTPConnection
from django.conf import settings
import os,csv,random
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

def register_user(request, dept_name="Events", owner_name = None):
    """
    for test phase the default dept is Events
    """
    print "this is the deptname user belongs to ",dept_name
    department = Group.objects.get (label__name = 'Department',
                                    name = dept_name)
    user_form = AddUserForm ()
    profile_form = userprofileForm ()
    if request.method=='POST':
        user_form = AddUserForm (request.POST)

        if user_form.is_valid():
            # Create the User
            new_user = User.objects.create_user(
                username = user_form.cleaned_data['username'],
                email = user_form.cleaned_data['email'],
                password = user_form.cleaned_data['password'],
                )    
            # Save his profile - mainly his dept name
            #here if must be changed to try
	    if True:
	        # department=Department.objects.get(Dept_Name = dept_name)
		profile=userprofile.objects.create(user=new_user)
                profile.save()
                #creating a folder for the user
                file_name="PROFILE_PIC_OF_THE_USER"
                savepath ,file_path=create_dir(file_name  , user_form.cleaned_data['username'])
                image_object=userphoto(name=new_user ,photo_path="http://localhost/django-media/upload_files/ee10b000/PROFILE_PIC_OF_THE_USER")
                image_object.save()
                print "created folder and given default user_profil_pic"
	    else:
		print "userprofile not saved ,check out"
            # Make the user a Coord
            new_user.groups.add (auth.models.Group.objects.get (name = 'Coords'))
            new_user.is_active=True #took from userportal
            new_user.save()
            registered_successfully = True
            request.session['just_registered'] = True
            return redirect ('home.views.login')
	else:
	    print "the user form is not valid the errors are :"
	    print user_form.errors
            return render_to_response('users/register.html' , locals() ,context_instance = global_context(request))
    else:
        return render_to_response('users/register.html' , locals() ,context_instance = global_context(request))

        
      


# WTH is this?

# def register_invite(request,dept_name="none" ,username="none" ,rollno="ee0b000"):
#     print "deptname :" ,dept_name
#     user_form = AddUserForm (initial={'username':rollno},)
#     return render_to_response('users/register.html' , locals() ,context_instance = global_context(request))


@needs_authentication
def invite(request ,owner_name):
    CsvForm=UploadFileForm(initial={'title':"Enter the name" , 'short_description':"you may write anything here"})
    message=[]
    message+=["start"]
    user_dept = request.user.get_profile ().get_dept ().name
    print user_dept
    success_message="" 
    if request.method=='POST':
        form=InviteForm(request.POST)
        if form.is_valid():
            message+=["form valid "]
            name=form.cleaned_data['invitee']
            emailid=form.cleaned_data['email_id']
            roll_no=form.cleaned_data['roll_no']
            

            # print settings.SITE_URL+"/users/register_invite/"+user_dept+"/"+name+"/"+roll_no+"/"
            invite_details=invitation(
            core=request.user,
            invitee=name,
            email_id=emailid,
            time=datetime.datetime.now(),
            )#this stores the information of invitation
            try:
                #here the essential mail details are assigned
                hyperlink=settings.SITE_URL+"/users/register_invite/"+user_dept+"/"+name+"/"+roll_no+"/"
                mail_header="Invitaiton from the core to join ERP"
                mail=[emailid,]
		print mail
                #sending mail here
                print "came till the function part"
                success_message=mail_coord(hyperlink ,mail_header ,name ,"users/emailcoords.html" ,mail ) 
          
             
            except:
                message+=["mail could not be sent "]
                success_message=["mail could not be sent may be wrong details"]
                print "mail not sent."
                pass

		
        

    else:
        message+=["form not valid"]
    invite_form=InviteForm()
    return redirect('tasks.views.display_portal',owner_name=owner_name)



"""
this part yet to be done
"""
@needs_authentication
def invite_inbulk(request ,owner_name):
    print "in invite bult function"
    form=InviteForm()
    CsvForm=UploadFileForm(initial={'title':"Enter the title" , 'short_description':"you may write anything here"})
    
    if request.method=='POST':
        form=UploadFileForm(request.POST,request.FILES)
    
        if True : #form.is_valid(): yet to check the file            
            file_name=request.FILES['file'].name
            user_name=request.user.username
            save_path ,file_path = create_dir(file_name ,user_name)#passing to the fuction to make directories if not made         
            date=datetime.datetime.now()

            try:
                file_present=upload_documents.objects.get(user=request.user,file_name=file_name)
                message="There is a file already with this name .please change the name of the file"
            except:
                f=request.FILES['file']
                write_file(save_path ,f)
		google_path="http://docs.google.com/viewer?url="+file_path
                file_object=upload_documents(user=request.user , file_name=file_name,file_path=file_path,google_doc_path=google_path,url=file_path ,topic="invitation to coords",date=date)#to change topic
                file_object.save()


            message="done"
            """ from here the the csv file is opened and the the coords are invited .yet to be asked and completed """
            
            reader=csv.reader(open(save_path,'rb'),delimiter=';')
            
	    user_dept = request.user.get_profile ().get_dept ()
            for field in reader:
            	"""
            	print field[0] #id
            	print field[1] #roll_no
            	print field[2]#email_id
            	print field[3]#name
            	"""
            	name=field[3]
            	roll_no=field[1]
            	emailid=email_id
                try:
                #here the essential mail details are assigned
		    hyperlink=settings.SITE_URL+"/users/register_invite/"+user_dept+"/"+name+"/"+roll_no+"/"
		    mail_header="Invitaiton from the core to join ERP"
		    mail=[emailid,]
		    #sending mail here
		    success_message=mail_coord(hyperlink ,mail_header ,name ,"users/emailcoords.html" ,mail ) 
		    
		     
		except:
		    message+=["mail could not be sent to"+name]
		    success_message=["mail could not be sent may be wrong details"]
		    print "mail not sent."
    return redirect('tasks.views.display_portal',owner_name=owner_name)

            
@needs_authentication
def view_profile(request, owner_name=None):
    page_owner = get_page_owner (request, owner_name)
    try:
        image=userphoto.objects.get(name=page_owner)
        photo_path =image.photo_path
    except:
        photo_path=settings.MEDIA_URL+"/upload_files/ee10b000/PROFILE_PIC_OF_THE_USER"
    profile = userprofile.objects.get(user=page_owner)
    print profile.nickname
    print profile.name
    return render_to_response('users/view_profile.html',locals(),context_instance = global_context(request))
    	


@needs_authentication
def handle_profile (request  , owner_name):
    print request.user.id , "is the id of the user"

    user = request.user
    profile = userprofile.objects.get(user=request.user)
    if request.method=='POST' :
        profile_form = userprofileForm (request.POST, instance = profile)
        if profile_form.is_valid ():
            profile_form.save ()
            # Should this just redirect to the dashboard?
	    return view_profile(request ,request.user.username)
        else: 
            print  profile_form.errors  
            return render_to_response('users/edit_profile.html' , locals() ,context_instance = global_context(request))
    print profile.hostel
    profile_form = userprofileForm (instance = profile)       
    print " default pic address http://localhost/django-media/upload_files/ee10b000/PROFILE_PIC_OF_THE_USER"
    try:
        image=userphoto.objects.get(name=request.user)
        photo_path =image.photo_path
        print photo_path
    except:
        photo_path=settings.MEDIA_URL+"/upload_files/ee10b000/PROFILE_PIC_OF_THE_USER"
    return render_to_response('users/edit_profile.html',locals(),context_instance = global_context(request))



def manage_circle(request ,owner_name=None):
    print "\n\n\n\n\n came in manage_circles "
    photo_id=0
    if request.method=="GET":
        print "peace max"	
        post = request.GET.copy()
	try:
	    work=post['work']
	    print "The work is ",work
	    
	    if work=="add_circles":
	        print "Adding circle work is confirmed"

	        new_circle_id=str("new_circle"+str(random.randint(1,4000))  )
	        new_circle=Circle.objects.create(user=request.user ,circle_name= new_circle_id)
	        new_circle.save()
	    elif work=="add_photos":
	        print "Adding photos to the circles"
	        circle_name=(post['circle_name'])
	        
	        photo_id=int(post['photo_id'][3:])
	        print "the circle name :- " ,circle_name
	        print "Photo id is :- ",photo_id
	        if len(circle_name)!=0:
	            circle_id=int(circle_name[6:])
	            print "the id of the circle is " ,circle_id
#		    curr_circle=Circle.object	
		    
    	            photo_added=userphoto.objects.get(id=photo_id)
    	            curr_circle=Circle.objects.get(id=circle_id)
	            print photo_added
#	            print curr_circle
		    curr_circle.circle_photo.add(photo_added)

	        	
	except:
	    print "There is error"

	  #      print photo_added
    user_circles=Circle.objects.filter(user=request.user)
    return render_to_response('users/circles.html',locals(),context_instance = global_context(request))
	
	
def manage_groups(request ,owner_name=None):
    print("in groups")
    
    return render_to_response('users/groups.html',locals(),context_instance = global_context(request))
def js_test(request,data="nothing yet"):
    print "\n\n\n\n\n came in js_test "
    print request.method
    if request.method=="GET":
        print "peace max"	
        post = request.GET.copy()
        try:
            print "this ",post['slug']
        except:
            print "no variable"
        for dum in post:
            print dum
        if "data" in request.GET:
            print "more peace"
    else:
        print "pain"
    
    print "came out in js_test \n\n\n\n\n\n\n"
    return render_to_response('users/js_test.html',locals(),context_instance = global_context(request))

    
