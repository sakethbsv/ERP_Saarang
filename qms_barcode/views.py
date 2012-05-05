# Create your views here.
from django.contrib import auth
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.template.context import Context, RequestContext
from django.utils import simplejson
from erp_test.misc.util import *
from erp_test.settings import *
from erp_test.qms_barcode.models import Participant, College , Event , Winners
from django.forms import ValidationError
from erp_test.qms_barcode import models
from erp_test.qms_barcode import forms
from erp_test.qms_barcode.forms import AddParticipantForm ,ShaastraIDForm ,OnlineRegForm
import sha,random,datetime
from django.forms.formsets import formset_factory
TEAM_LABEL = "Participant Team"
from django.db.models import Q

def coord_barcode_login(request):
	login_form = forms.BarcodeLogin()	
	if request.method == "POST":
		data = request.POST.copy()
		login_form = forms.BarcodeLogin(data)
		if login_form.is_valid():
			user = auth.authenticate(username = login_form.cleaned_data['username'],
										password = login_form.cleaned_data['password'])
			if user is not None and user.is_active == True:
				auth.login(request , user)
				request.session['loggen_in'] = True
				if request.user.groups.filter (name = 'QMS_Reg'):
				  	is_qms 	= True
				  	is_event	= False
				  	is_ppm = False
				  	reg_form = forms.AddParticipantForm()
				  	colls = models.College.objects.all()
    					collnames = list()
    					for coll in colls:
        		                    collnames.append(coll.name + "," + coll.city)
   					js_data = simplejson.dumps(collnames)
                                        online_reg_form = forms.OnlineRegForm()
				  	#event_form = forms.EventRegForm()
				  	return render_to_response('barcode/register_participant.html', locals(), context_instance= global_context(request))    
				if request.user.groups.filter (name = 'Event_Reg'):        
				        reg_form = forms.BarcodeRegisterForm()
				       	is_qms		= False
				       	is_event	= True
				       	is_ppm 	= False
					event = Event.objects.all()
					event_list=[]
					for e in event:
					    event_list.append(str(e))
					event_list = simplejson.dumps(event_list)
					return render_to_response('barcode/regpage.html',locals(),  context_instance= global_context(request))
				if request.user.groups.filter (name = 'ppm_Reg'):        
				        reg_form = forms.BarcodeRegisterForm()
				       	is_qms	= False
				       	is_event	= False
				       	is_ppm 	= True
				  	event = Event.objects.all()
					event_list=[]
					for e in event:
					    event_list.append(str(e))
					event_list = simplejson.dumps(event_list)
				  	return render_to_response('barcode/ppm.html', locals(), context_instance= global_context(request))    
				
			else:
				invalid_login_message = "enter the login details or contact the webops junta now"
				request.session['invalid_login'] =True

  	return render_to_response('barcode/barcode_login.html', locals(), context_instance= global_context(request))    

def logout(request):

    if request.user.is_authenticated():
        auth.logout (request)
    login_form = forms.BarcodeLogin()	
    return render_to_response('barcode/barcode_login.html', locals(), context_instance= global_context(request))

@needs_authentication
def participant_register(request):
    """ 
        Retrieve the list of colleges and display them as coll.name,coll.city . This list is used for the jquery autocompletion. 
        js_data is a simplejson dump of the list of collnames. 
        
        ...var data = {{js_data|safe}};
        ...$("#coll_input").autocomplete(data);
        
        These two lines in the template handle the autocomplete for college selection. ( The id of the college field is set to coll_input in forms.py. You need to include the jquery autocomplete plugin for it to work.
    """ 
    reg_form = forms.AddParticipantForm()    
    online_reg_form = forms.OnlineRegForm()
    reg_form = forms.AddParticipantForm()
    message = ""
    display_errors = True
    if not request.user.groups.filter (name = 'QMS_Reg'):
       	login_form = forms.BarcodeLogin()	
        cheat_message = "You cannot handle QMS Data , THIS will be reported "
  	return render_to_response('barcode/barcode_login.html', locals(), context_instance= global_context(request))    
    colls = models.College.objects.all()
    collnames = list()
    for coll in colls:
        #print coll
        collnames.append(coll.name + "," + coll.city)
   
    js_data = simplejson.dumps(collnames)
    if request.method=='GET':
        data = request.GET.copy()
        online_reg_form = forms.OnlineRegForm(data)
        if online_reg_form.is_valid():
            username_already = online_reg_form.cleaned_data['username']
            #print username
            try:
                print "Here1"
                participant_object = Participant.objects.get(username = username_already)
                participant_object.username = ""
                participant_object.college_id = "" 
                reg_form = forms.AddParticipantForm(instance = participant_object )    
                print reg_form
                message = ""
            except:
                message = "User with this name doesnt exists in online database"
            
            
           
    if request.method=='POST':
        
        data = request.POST.copy()
        username=data['username']
        if not username.isdigit() and len(username)!=8 and not 'registered' in data:
            if not data['first_name']:
                  data['first_name']= username
            data['college']='IIT-Madras,Chennai'
            
	reg_form = forms.AddParticipantForm(data)        
	if 'registered' in data:
	    username_already = data['registered']
            reg_user = Participant.objects.get(username=data['registered'])
            reg_form = forms.AddParticipantForm(data, instance=reg_user)
            if reg_form.is_valid():
                  reg_form.save()
                  message = "Previous participant registered"
                  
                 
        elif reg_form.is_valid():
            
	    username = reg_form.cleaned_data['username']                 
            participant = Participant(
                    username= reg_form.cleaned_data['username'],                   
	            email = reg_form.cleaned_data['email'],
                    first_name=reg_form.cleaned_data['first_name'],
                    mobile     = reg_form.cleaned_data['mobile'],
	            college     = reg_form.cleaned_data['college'],
                    gender     = reg_form.cleaned_data['gender'],
	            branch     = reg_form.cleaned_data['branch'],
		    degree     = reg_form.cleaned_data['degree'],
		    year     = reg_form.cleaned_data['year'],
                    )
            message = "The is error in the data please check it once more"
            participant.save()
            message = "Previous participant registered"
        else: 
 	    return render_to_response('barcode/register_participant.html', locals(), context_instance= global_context(request))    	        
	    

	    
	    print request.POST['username']
	    try:
	        participant_object = Participant.objects.get(username = username )
	        participant_object.email = 	request.POST['email']    
	        participant_object.first_name = 	request.POST['first_name']
	        participant_object.mobile = 	request.POST['mobile']
	        participant_object.gender = 	request.POST['gender']
	        participant_object.branch = 	request.POST['branch']
	        participant_object.degree = 	request.POST['degree']
	        participant_object.year = 	request.POST['year']
		message = "The previous participant has now assigned his barcode"
		display_errors = False

	        participant_object.save()
	        
	    except:
	        pass
	        

    is_qms    = True
    is_event  = False
    is_ppm 	= False 
    online_reg_form = forms.OnlineRegForm()

    #event_form = forms.EventRegForm()
    return render_to_response('barcode/register_participant.html', locals(), context_instance= global_context(request))    
       	    
@needs_authentication
def search(request):
    result= True
    form=forms.SearchForm()
    if request.method== 'POST' :
        data=request.POST.copy()
        form=forms.SearchForm(data)
 
        if form.is_valid() :
        
           
            sbarcode=form.cleaned_data['barcode']
            sname=form.cleaned_data['name']
            smobile=form.cleaned_data['mobile']
            
            if sbarcode and sname and smobile:
            	results=models.Participant.objects.filter(Q(username__icontains=sbarcode) | Q(first_name__icontains=sname) | Q(mobile__icontains=smobile))
            elif sbarcode and sname:
				results=models.Participant.objects.filter(Q(username__icontains=sbarcode) | Q(first_name__icontains=sname))
            elif sbarcode and smobile:
            	results=models.Participant.objects.filter(Q(username__icontains=sbarcode)| Q(mobile__icontains=smobile))
            elif sname and smobile:
				results=models.Participant.objects.filter(Q(first_name__icontains=sname) | Q(mobile__icontains=smobile))
            elif sbarcode:
				results=models.Participant.objects.filter(username__icontains=sbarcode)
            elif sname:
				results=models.Participant.objects.filter(first_name__icontains=sname)
            elif smobile:
				results=models.Participant.objects.filter(mobile__icontains=smobile)
            else:
		    	results=[]
				            
            
            if results:
            	result=True
            else:
            	result_cup=True	        
             
    return render_to_response('barcode/search_form.html', locals(), context_instance= global_context(request))    


@needs_authentication
def participant_update(request):

    
    if request.method=='GET':
        user=models.Participant.objects.get(username=request.GET['barcode'])
        print user
        win=Winners.objects.filter(winner=user)
        	
    if request.method=='POST':
        if request.method=="POST":
            user=models.Participant.objects.get(username=request.POST['barcode'])
        update_form = forms.EditUserForm(request.POST, instance = user) 
           
        if update_form.is_valid() :
            update_form.save()
            form=forms.SearchForm()

            return render_to_response('barcode/search_form.html' , locals() ,context_instance = global_context(request))
    update_form =forms.EditUserForm(instance = user)
    return render_to_response('barcode/update_profile.html', locals(), context_instance= global_context(request))    


@needs_authentication
def events_reg(request):
    event = models.Event.objects.all()
    event_list=[]
    for e in event:
        event_list.append(str(e))
    event_list = simplejson.dumps(event_list)
    if request.method == "POST":
    	if 'update' in request.POST:
	    e_name = request.POST['event_name']
	    if len(e_name)!=0:
	        request.session['event']=e_name
	    else:
	        message = "Please enter a correct event in the box"
	        
	elif 'teams' in request.POST:
	    e_name = request.session['event']
	    event = Event.objects.get(name=e_name)
	    grp_event = event.group_ptr_id
	    get_formset = formset_factory(forms.BarcodeRegisterForm)
	    barcode_formset = get_formset(request.POST)
	    if barcode_formset.is_valid():
	        label = Label.objects.get(name=TEAM_LABEL)
		team = Group(label=label)
		team.save()
		flag = 0
		for form in barcode_formset:
		    if 'barcode' in form.cleaned_data:		       
			username = form.cleaned_data['barcode']
			if(len(username)!=0):
			    flag = 1
		        user = User.objects.get(username = username)
		        try:
		            team.members.add(user)
		        except:
		            message = "The user has already been registered"
		team.parent = Group.objects.get(id=grp_event)
		if 'is_iitm' in request.POST:
		    if request.POST['is_iitm']:
		    	team.name="IIT-M Team"
		    	event.count_team_iitm = event.count_team_iitm + 1
		else:
		    team.name="Non IIT-M Team"
		    event.count_team = event.count_team + 1
		    
	            
		if flag == 1:
		    event.save()
		    team.save()
		else:
		    message="Please enter the participant's barcode/roll no"
	    else:
	        event_def = event.name
                return render_to_response('barcode/regpage.html',locals (),context_instance=global_context(request))
	    e_name = request.session.get('event', 'None') 
	    
	    
        elif 'addplace' in request.POST:
            try:
            	e_name = request.POST['event_name']
                request.session['event']=e_name
                e_name = request.session['event']
                event = Event.objects.get(name=e_name)
                grp_event = event.group_ptr_id
                print "Reached here finally"
                barcode_formset = formset_factory(forms.BarcodeRegisterForm, extra=event.cap_team, max_num = event.cap_team)
                display_place=True
                event_def = event.name

            except:
                message="Please enter the event in the box"
                
            return render_to_response('barcode/ppm.html',locals (),context_instance=global_context(request))                
            
            
        elif 'show_details' in request.POST:
            e_name = request.session['event']
            eventid = Event.objects.get(name=e_name)
            grp_event = eventid.group_ptr_id
            print "Reached here finally 2"
            get_formset = formset_factory(forms.BarcodeRegisterForm)
            event_def = eventid.name
            barcode_formset = get_formset(request.POST)            
            show_details_participants=True
            display_place=True
            users=list()
            if barcode_formset.is_valid():
                for form in barcode_formset:
                    if 'barcode' in form.cleaned_data:		       
                        user = Participant.objects.get(username = form.cleaned_data['barcode'])
                        users.append(user)
                print users
                return render_to_response('barcode/ppm.html',locals (),context_instance=global_context(request))        
            return render_to_response('barcode/ppm.html',locals (),context_instance=global_context(request))                     

            
        elif 'place' in request.POST:

            e_name = request.session['event']
            eventid = Event.objects.get(name=e_name)
            grp_event = eventid.group_ptr_id
            display_place=True
            event_def = eventid.name
            get_formset = formset_factory(forms.BarcodeRegisterForm)
            barcode_formset = get_formset(request.POST)            
            check=Winners.objects.filter(event=eventid, is_place=request.POST['place'])
            if check:
                already_filled=True
                display_place=True
                return render_to_response('barcode/ppm.html',locals (),context_instance=global_context(request))        
                
            winner_team=Winners(event=eventid,is_place=request.POST['place'])
            winner_team.save()
            flag = 0
            if barcode_formset.is_valid():
                for form in barcode_formset:
                    if 'barcode' in form.cleaned_data:		       
			username = form.cleaned_data['barcode']            	
			print username
			if(len(username)!=0):
			     flag = 1	  
                             print "Hello"
                        user = Participant.objects.get(username = username)
                        try:
                            winner_team.winner.add(user)
                        except:
			    message = "The user has not registered for the event. Any problem, contact the event coord"
                            pass
                if flag:
                    winner_team.save()        
                else:
                    winner_team.delete()
                    message = "There is no barcode/roll numbers given "
            barcode_formset = formset_factory(forms.BarcodeRegisterForm, extra=eventid.cap_team, max_num = eventid.cap_team)
            return render_to_response('barcode/ppm.html',locals (),context_instance=global_context(request))
            
            
        elif 'export_winners' in request.POST:
	    try:
		    e_name = request.session['event']
		    eventid = Event.objects.get(name=e_name)
		    grp_event = eventid.group_ptr_id
		    event_def = eventid.name
		    check=Winners.objects.filter(event=eventid)
		    cap_team=list()
		    l=eventid.cap_team
		    
		    while l!=0:
		        cap_team.append('1')
		        l=l-1
		        
		    print check
	    except:
	    	message = "Please enter a correct event in the box"
	        pass
            return render_to_response('barcode/ppm.html',locals (),context_instance=global_context(request))
            
            
        elif 'edevent' in request.POST:
            try:
	        e_name = request.POST['event_name']
	        request.session['event']=e_name
	        event = Event.objects.get(name=e_name)
	        ev_edit_form = forms.EventEditForm(instance=event) 
	    except:
	    	message = "Please enter an event or change the name of the event in the box"
	    
	    
        elif 'updateEvent' in request.POST:
	    try:
   	        data=request.POST.copy()
	        e_name = request.session.get('event', '')
	        event = Event.objects.get(name=e_name)
	        ev_edit_form = forms.EventEditForm(data, instance=event) 
	        if ev_edit_form.is_valid():
	            ev_edit_form.save()
	    	    del(ev_edit_form)
	    except:
	        message = "Please enter a correct event in the box"
	        pass
			        	 


	elif 'export' in request.POST:
            if request.POST['event_name']:
                print "reached"
                return HttpResponseRedirect('%s/' %(request.POST['event_name']))
            else:
                message= "Please enter a correct event in the box"
	try:
            event_def = e_name
	    event = Event.objects.get(name=e_name)
            barcode_formset = formset_factory(forms.BarcodeRegisterForm, extra=event.cap_team, max_num = event.cap_team)
		    
            no_iitm_team_waiting = event.count_team_iitm - event.cap_iitm
            if(no_iitm_team_waiting < 1):
                no_iitm_team_waiting=0
	    else:
	        message = "The team is wait listed"
            no_non_iitm_team_waiting = event.count_team -  event.cap_non_iitm
            if(no_non_iitm_team_waiting < 1):
                no_non_iitm_team_waiting=0		        
	    else:
	        message = "The team is wait listed"	                            
	except:
            message = "Please enter a correct event in the box"	
	    pass
    else:
        event_def=request.session.get('event', '')
    	if event_def:
	    event = Event.objects.get(name=event_def)
    

    return render_to_response('barcode/regpage.html',locals (),context_instance=global_context(request))

@needs_authentication
def show_details(request, event):
    print event
    try:
	    event = Event.objects.get(name = event)
	    label = Label.objects.get(name = TEAM_LABEL )
	    teams = event.children_set.filter(label = label)
	    team_cap = event.cap_team
	    print team_cap
	    show_teams="</tr><tr><td>No. of teams Non-INSTI </td><td> %s</td></tr><tr><td>No. of teams INSTI </td><td> %s</td></tr>" %(event.count_team, event.count_team_iitm)
	    for team in teams:
		show_teams=show_teams+"<tr>"
		count = 0
		for u in team.members.all():
		    count +=1
		    show_teams=show_teams+"<td>%s</td>" %u
		for x in xrange(team_cap-count):
		    show_teams=show_teams+"<td>""</td>"         
		show_teams=show_teams+"<td>%s</td>"%(team.name)	
		show_teams=show_teams+"</tr>"
	    print show_teams
            return render_to_response('barcode/viewteams.html',locals (),context_instance=global_context(request))	    
    except:
	message = "Please correct enter an event in the box"
    return render_to_response('barcode/regpage.html',locals (),context_instance=global_context(request))
    	
def help_text(request):
    return render_to_response('barcode/help_content.html',locals (),context_instance=global_context(request))

def college_registration (request):
    if request.method == 'POST':
        data = request.POST.copy()
        coll_form = forms.AddCollegeForm(data)
        print coll_form
        if coll_form.is_valid():
            college=coll_form.cleaned_data['name']
            print "Valid"
            if college.find('&')>=0:
                college = college.replace('&','and')
            city=coll_form.cleaned_data['city']
            state=coll_form.cleaned_data['state']
            
            if len (College.objects.filter(name=college, city=city, state=state))== 0 :
                college=College (name = college, city = city, state = state)
                college.save()
                data = college.name+","+college.city
                           
    else:
        coll_form=forms.AddCollegeForm()        
    return render_to_response('barcode/register_college.html', locals(), context_instance= global_context(request))        
    
