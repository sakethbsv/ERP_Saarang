
# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.template.loader import get_template
from django.template.context import Context, RequestContext
from django.forms.models import modelformset_factory, inlineformset_factory
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
import datetime
from forms import *
from models import *
from erp_test.misc.util import *
from django.core.mail import send_mail,EmailMessage,SMTPConnection
from erp_test.misc.helper import is_core, is_coord,is_supercoord,  get_page_owner, delete_this_file
# from erp_test.department.models import *
from erp_test.settings import SITE_URL
from erp_test.dashboard.forms import shout_box_form
from erp_test.dashboard.models import shout_box
from erp_test.users.forms import InviteForm ,UploadFileForm
import datetime
from django import forms

# 
def calculate_sums(data):
    """
    Calculates sums of the 3 tuple data with fields amount_a, amount_b and amount_revised
    """
    try:
        sum_amount_a=sum([x[0] for x in data.values_list('amount_a')])
    except:
        sum_amount_a=0
    try:
        sum_amount_b=sum([x[0] for x in data.values_list('amount_b')])
    except:
        sum_amount_b=0
    try:
        sum_amount_r=sum([x[0] for x in data.values_list('amount_revised')])
    except:
        sum_amount_r=0
    return sum_amount_a, sum_amount_b, sum_amount_r

def calculate_budget(total,balance):
    """
    Calculates Total budget for an event, and amount of balance money left
    """
    try:
        total=sum([x[0] for x in total.values_list('amount_revised')])
    except:
        total=0

    balance_val = 0
    try:
        for item in balance:
            try:
                balance_val += item.amount_request
            except:
                pass
    except:
        pass
    balance_val = total - balance_val
    return total,balance_val
def get_supercoord_events():
    pass

def get_all_events():
    """
    Gets a list of all events in the format eventName, sum_amount_a,
    sum_amount_b sum_amount_revised, earliest_deadline
    """
    
    
    all_events = Group.objects.filter (label__name = 'Event')
    all_data = []
    for item in all_events:
        data = []
        event_data = Budget_Event.objects.filter (event = item)
        sum_amount_a,sum_amount_b,sum_amount_r = calculate_sums(event_data)        
        print event_data
        try:
            earliest_deadline = event_data[0].requirement_date
        except:
            earliest_deadline = None
        for subitem in event_data:
            if earliest_deadline > subitem.requirement_date:
                earliest_deadline = subitem.requirement_date
#            userdata = []
#           userdata.append(item.user)
#            userdata.append(item.department)
        #            all_user_data.append(userdata)
        data.append(item.name)
        data.append(sum_amount_a)
        data.append(sum_amount_b)
        data.append(sum_amount_r)                
        data.append(earliest_deadline)
        all_data.append(data)
    return all_data


def get_all_eventsadvanceportal():
    """
    This is to get events data for advance payment portal.
    Output Format: eventName, totalBudget, balanceBudget, rejectedBudget,
    earliestDeadline.
    """
    all_events = Group.objects.filter (label__name = 'Event')
    all_data = []
    for item in all_events:
        data = []
        accepted_requests_A = Budget_Event.objects.filter(event = item, status='A')
        required_items = Budget_Event.objects.filter(event = item)
        advance_payment_objs = []
        rejected_objs = []
        for item2 in accepted_requests_A:
            advance_payment_objs += Advance_Payment.objects.filter(link = item2, finance_approval=True)
            rejected_objs += Advance_Payment.objects.filter(link = item2, finance_approval=False)
            
        total_budget, balance_budget_total = calculate_budget(accepted_requests_A, advance_payment_objs)
        total_budget, rejected_budget_total = calculate_budget(accepted_requests_A, rejected_objs)        
        rejected_budget_total = total_budget - rejected_budget_total
        event_data = Budget_Event.objects.filter(event = item)
        try:
            earliest_deadline = event_data[0].requirement_date
        except:
            earliest_deadline = None
        for subitem in event_data:
            if earliest_deadline > subitem.requirement_date:
                earliest_deadline = subitem.requirement_date
#            userdata = []
#           userdata.append(item.user)
#            userdata.append(item.department)
        #            all_user_data.append(userdata)
        data.append(item.name)
        data.append(total_budget)
        data.append(balance_budget_total)
        data.append(rejected_budget_total)                
        data.append(earliest_deadline)
        all_data.append(data)
    return all_data

def get_all_departments():
    """
    Unused as only event budgets are required.
    Functionality is same as get_all_events
    """
    all_depts = Group.objects.filter (label__name = 'Department')
    all_data = []

    for item in all_depts:
        if str(item.name) != "Events" and str(item.name) != "Finance":
            data = []
            dept_data = Budget_Department.objects.filter(department=item)
            sum_amount_a,sum_amount_b,sum_amount_r = calculate_sums(dept_data)
            try:
                earliest_deadline = dept_data[0].requirement_date
            except:
                earliest_deadline = None
            for subitem in dept_data:
                if earliest_deadline > subitem.requirement_date:
                    earliest_deadline = subitem.requirement_date
            data.append(item.name)        
            data.append(sum_amount_a)
            data.append(sum_amount_b)
            data.append(sum_amount_r)                
            data.append(earliest_deadline)
            all_data.append(data)
    return all_data



@needs_authentication
def financecoord(request,is_event=0,department="",owner_name=None,edit=False):
    """
    This function is called if a finance coord logs in. It sets the finance coord flag.
    Accordingly, depending on whether he is viewing an events finance page, or another departments,
    the respective function is called.
    """
    print "Dept",department
    finance_coord = True
    is_event = int(is_event)
    if is_event:
        return eventcoord(request,department,request_id=-1,owner_name=owner_name,Edit=False)
    else:
        return finance(request,request_id=-1,department_str=department,portal=None,owner_name=owner_name,edit=False)        
    return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))


def process_advance_finance(request, owner_name=None,event=""):
    pass
    return process_advance(request,owner_name,event)
    
def process_advance(request, owner_name=None,event=""):
    """
    This function takes care of Advance Payment Portal.
    Each event has a separate page. 
    """
    # CHANGE : MACHAN, WHAT ARE YOU DOING HERE???? Should this be department__in
    # https://docs.djangoproject.com/en/dev/ref/models/querysets/#in
    accepted_requests_A = Budget_Event.objects.filter(event = Group.objects.filter(label__name = 'Event', name=event), status='A')
    accepted_requests_A_list = accepted_requests_A.values_list('id', 'amount_revised')    
    form = AdvancePortalForm
    if request.method == 'POST':
        for item in accepted_requests_A_list:
            subitems = Advance_Payment.objects.filter(link=item[0])
            currentform = form(request.POST, prefix=str(item[0]))
            if currentform.is_valid():
                # Checks amount_request and adds a new row to the table stating the requested amount
                new_val = currentform.cleaned_data['amount_request']
                if new_val != 0 and new_val != "" and new_val != None:
                    new_val = int(new_val)
                    print "n", new_val                    
                    exist = Advance_Payment(link=Budget_Event.objects.get(id=item[0]))
                    all_requests = Advance_Payment.objects.filter(link=Budget_Event.objects.get(id=item[0]), finance_approval=True)
                    balance = item[1] - sum([x[0] for x in all_requests.values_list('amount_request')])
                    print "b" , balance
                    if new_val <= balance: 
                        exist.amount_request = new_val
                        exist.save()

            bufferform = BufferForm(request.POST)
            # Checks and adds buffer form
            if bufferform.is_valid():
                try:
                    exist = Buffer.objects.get(event = Group.objects.get (label__name = 'Event',
name = event))
                    exist.reason = bufferform.cleaned_data['reason']
                    exist.finance_approval = False
                    exist.amount_request = bufferform.cleaned_data['amount_request']
                    exist.save()

                except:
                    exist = Buffer()
                    exist.reason = bufferform.cleaned_data['reason']
                    exist.amount_request = bufferform.cleaned_data['amount_request']
                    exist.event = Group.objects.get (label__name = 'Event',
name = event)
                    exist.save()
            for item in subitems:
                # Checks and adds approvals amount requested
                boolform = BoolForm(request.POST, prefix=(item.id))
                if boolform.is_valid():
                    try:
                        exist = Advance_Payment.objects.get(id=item.id)
                        exist.finance_approval = boolform.cleaned_data['bool_val']
                        exist.save()
                    except:
                        exist = Advance_Payment(link=Budget_Event.objects.get(id=item[0]))
                        exist.finance_approval = boolform.cleaned_data['bool_val']
                        exist.amount_request = 0
                        exist.save()
            
            boolform = BoolForm(request.POST, prefix=("bufferfin"))
            # Checks and adds approvals for buffer
            if boolform.is_valid():
                try:
                    exist = Buffer.objects.get(event=Group.objects.get (label__name = 'Event',
name = event))
                    exist.finance_approval = boolform.cleaned_data['bool_val']
                    exist.save()
                except:
                    exist = Buffer(event=Group.objects.get (label__name = 'Event',
name = event))
                    exist.finance_approval = boolform.cleaned_data['bool_val']
                    exist.amount_request = 0
                    exist.save()
    user = request.user
    message = 'Event '+event+' has submitted requests in the advance payment portal.'
#    send_mail ('Event '+event+ ' has submitted requests', message, 'noreply@shaastra.org', ['prakruthi031@gmail.com','nikhil.agrawal020@gmail.com','mvjairaj@gmail.com','jackadimathara@gmail.com'])
    a = send_mail ('Event '+event+ ' has submitted requests', message, 'noreply@shaastra.org', ['mvijaykarthik@gmail.com'])
    print a
    print message
    print "\n\n\n\n\n\n\n"
    if str(user.get_profile().get_dept ()) == "Events":
        print "ZZZZZZZZZZZZZz", event
        return HttpResponseRedirect("../")        
    else:
        return HttpResponseRedirect("../")

#    return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))
@needs_authentication
def eventcoord(request,event="",request_id=-1,owner_name=None,Edit=False):
    """
    Function called when an event coord logs in. Displays his requests.
    Allows him to add new requests for his event.
    Each event has a separate page
    """
    
    event_name = event
    event_coord = True
    user = request.user
    coordinating = Group.objects.filter(label__name = 'Events', members = user)
    page_owner = get_page_owner (request, owner_name)    
    
    for item in coordinating:
        if event in str(item.name):
            allow_adding_request = True
    Form = BudgetFormEvent
    if str(user.get_profile().get_dept ()) == "Finance":
        finance_coord=True
        allow_adding_request = True
        all_events_data = get_all_events()
        all_department_data = get_all_departments()
        Form = BudgetFormCoordEvent
    else:
        finance_coord=False
    if (str(user) != str(page_owner)):
        allow_adding_request = False
    if event == "":
        event_list = []
        for item in coordinating:
            
            event_list.append(item.name)
        return render_to_response('finance/select_event.html',locals(), context_instance = global_context (request))        
    finance_form = Form()
    advance_portal_finance_data = get_all_eventsadvanceportal()
    # Get requests created by an event
    self_requests = Budget_Event.objects.filter(event = Group.objects.filter(label__name = 'Events', name = event))
    accepted_requests_A = Budget_Event.objects.filter(event = Group.objects.filter(label__name = 'Events', name = event), status='A')
    required_items = Budget_Event.objects.filter(event=Group.objects.get (label__name = 'Event',
name = event))
    advance_payment_objs = []
    for item in accepted_requests_A:
        advance_payment_objs += Advance_Payment.objects.filter(link = item, finance_approval=True)

    total_budget, balance_budget_total = calculate_budget(accepted_requests_A, advance_payment_objs)
    
    accepted_requests_A_list = accepted_requests_A.values_list('id', 'amount_revised')
    string_r_A = {}
    status_A = {}
    form_tuple = []
    ids_A = []
    try:
        buffer_exist = Buffer.objects.get(event=Group.objects.get (label__name = 'Event',
name = event))
        if buffer_exist.finance_approval == True:
            buffer_approved=True
    except:
        pass
    for i in range(0, len(accepted_requests_A_list)):
        # Get data to be displayed on advance payment portal
        all_approved_requests = Advance_Payment.objects.filter(link=Budget_Event.objects.get(id=accepted_requests_A_list[i][0]), finance_approval=True)
        balance_budget = accepted_requests_A_list[i][1] - sum([x[0] for x in all_approved_requests.values_list('amount_request')])
        not_approved_objs = Advance_Payment.objects.filter(link=Budget_Event.objects.get(id=accepted_requests_A_list[i][0]), finance_approval=False)
        all_objs_for_item = Advance_Payment.objects.filter(link=Budget_Event.objects.get(id=accepted_requests_A_list[i][0]))
        not_approved_amt = sum([x[0] for x in not_approved_objs.values_list('amount_request')])
        temp = []
        ids_A.append(accepted_requests_A_list[i][0])
#        money[accepted_requests_A_list[i][0]] = AdvancePortalForm(prefix=str(accepted_requests_A_list[i][0]))
        money = AdvancePortalForm(prefix=str(accepted_requests_A_list[i][0]))

        boolformfin = BoolForm(prefix=str(accepted_requests_A_list[i][0])+"fin")
        boolformeven = BoolForm(prefix=str(accepted_requests_A_list[i][0])+"even")        
        temp.append(accepted_requests_A[i])
        temp.append(money)

        try:
            filteritem = Budget_Event.objects.get(id=accepted_requests_A_list[i][0])
            exist = Advance_Payment.objects.get(link=filteritem)
            Advance_object = exist
        except:
            exist = Advance_Payment(amount_request=0, link=filteritem)
        try:
            if exist:
                status_A = accepted_requests_A_list[i][1] - exist.amount_request
            else:
                status_A = accepted_requests_A_list[i][1]
        except:
            pass
        temp.append(status_A)
        try:
            temp.append(exist.amount_request)
        except:
            temp.append(0)
        if (is_core(user) and finance_coord):
            d = {}            
            user_is_core = True
            try:
                if(exist.finance_approval == False):
                    temp.append(boolformfin)
                else:
                    d['bool_val']="Approved"                    
                    temp.append(d)
                    d = {}
                    
                if(exist.events_approval == False):
                    d['bool_val']="Not yet Approved"                    
                    temp.append(d)
                    d = {}                    
                    
                else:
                    d['bool_val']="Approved"                                        
                    temp.append(d)
                    d = {}                    
            except:
                temp.append(boolformfin)
                d['bool_val']="Not yet Approved"                
                temp.append(d)
                d = {}                

        elif (is_core(user)):
            d = {}
            user_is_core = True
            try:
                if(exist.finance_approval == False):
                    d['bool_val']="Not yet Approved"
                    temp.append(d)
                    d = {}                    
                else:
                    d['bool_val']="Approved"
                    temp.append(d)
                    d = {}                                        
                if (exist.events_approval == False):
                    temp.append(boolformeven)                
                else:
                    d['bool_val']="Approved"                    
                    temp.append(d)
                    d = {}                    
            except:
                temp.append("Not yet Approved")
                temp.append(boolformeven)
        else:
            d = {}
            if(exist.finance_approval == False):
                d['bool_val']="Not yet Approved"                                    
                temp.append(d)
                d = {}                                    
            else:
                d['bool_val']="Approved"                                    
                temp.append(d)
                d = {}                                    
            if (exist.events_approval == False):
                d['bool_val']="Not yet Approved"                                                    
                temp.append(d)
                d = {}                                    
            else:
                d['bool_val']="Approved"                                    
                temp.append(d)
                d = {}
        now = datetime.date.today()
        due = filteritem.requirement_date
        try:
            if Advance_object.finance_approval:
                temp.append("Accepted")
            else:
                temp.append("Available")
            Advance_object = []
        except:
            if (now > due):
                temp.append("Rejected")
            else:
                temp.append("Available")
            
        temp.append(not_approved_amt)

        temp3 = []
        for item in all_objs_for_item:
            temp2 = []
            temp2.append(item)
            if item.finance_approval == True:
                dicta = {}
                dicta['bool_val'] = "Approved"
                temp2.append(dicta)
            else:
                if (is_core(user)):
                    temp2.append( BoolForm(prefix=str(item.id)))
                else:
                    dicta = {}
                    dicta['bool_val'] = "Not Approved"
                    temp2.append(dicta)
            if (item.finance_approval == True):
                temp2.append("Accepted")
            elif (now > due):
                temp2.append("Rejected")
            else:
                temp2.append("Available")
            temp3.append(temp2)
        temp.append(temp3)
        temp.append(balance_budget)
        form_tuple.append(temp)
        
    temp = []
    # For Buffer in Advance payment Portal
    bufferform = []
    bufferform.append(BufferForm())
    # For Buffer
    temp = []
    buffer_A = []
    try:
        exist = Buffer.objects.get(event=Group.objects.get (label__name = 'Event',
name = event))
    except:
        exist = Buffer(event=Group.objects.get (label__name = 'Event',
name = event))	
    buffer_A = []
    buffer_A.append(exist)
    # If core, then allow him to approve requests.
    if (is_core(user) and finance_coord):
        d = {}            
        user_is_core = True
        try:
            if(exist.finance_approval == False):
                temp.append(BoolForm(prefix=str("bufferfin")))                                    
            else:
                d['bool_val']="Approved"                    
                temp.append(d)
                d = {}                                        
            if(exist.events_approval == False):
                d['bool_val']="Not yet Approved"                    
                temp.append(d)
                d = {}                                        
            else:
                d['bool_val']="Approved"                                        
                temp.append(d)
                d = {}                                        
        except:
            temp.append(boolformfin)
            d['bool_val']="Not yet Approved"                
            temp.append(d)
    elif (is_core(user)):
        d = {}
        user_is_core = True
        try:
            if(exist.finance_approval == False):
                d['bool_val']="Not yet Approved"
                temp.append(d)
                d = {}                                        
            else:
                d['bool_val']="Approved"                    
                temp.append(d)
                d = {}                                        
            if (exist.events_approval == False):
                temp.append(BoolForm(prefix=str("buffereven")))                
            else:
                d['bool_val']="Approved"                    
                temp.append(d)
                d = {}                                        
        except:
            temp.append("Not yet Approved")
            temp.append(BoolForm(prefix=str("buffereven")))                                                
    else:
        d = {}
        if(exist.finance_approval == False):
            d['bool_val']="Not yet Approved"                                    
            temp.append(d)
            d = {}                                                        
        else:
            d['bool_val']="Approved"                                    
            temp.append(d)
            d = {}                                                        
        if (exist.events_approval == False):
            d['bool_val']="Not yet Approved"                                                    
            temp.append(d)
            d = {}                                                        
        else:
            d['bool_val']="Approved"                                    
            temp.append(d)
            d = {}


# Amount Requested

            
    buffer_A.append(temp)
    sum_amount_a,sum_amount_b,sum_amount_r = calculate_sums(self_requests)    

    if request_id >= 0:
        request_to_edit = Budget_Event.objects.get (id = request_id)
        Edit = True
        finance_form = Form(initial={'particular':request_to_edit.particular, 'requirement_date':request_to_edit.requirement_date, 'amount_a':request_to_edit.amount_a, 'amount_b':request_to_edit.amount_b, 'amount_revised':request_to_edit.amount_revised, 'status':request_to_edit.status})
        if request.method == 'POST':        
            finance_form = Form(request.POST)
            if finance_form.is_valid():
                request_to_edit.particular = finance_form.cleaned_data['particular']
                request_to_edit.requirement_date = finance_form.cleaned_data['requirement_date']
                request_to_edit.amount_a = finance_form.cleaned_data['amount_a']
                request_to_edit.amount_b = finance_form.cleaned_data['amount_b']
                success = True
                if finance_coord:
                    request_to_edit.amount_revised = finance_form.cleaned_data['amount_revised']
                    request_to_edit.status = finance_form.cleaned_data['status']                    
                request_to_edit.save()
                request_id = -1
                return HttpResponseRedirect("./")
        return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))
#    return redirect ('finance.views.finance', locals())
    print "nearing"
    if request.method == 'POST':
        finance_form = Form(request.POST)
        print "saving"
        if finance_form.is_valid():
            new_request = finance_form.save (commit = False)
            success = True
            new_request.requester = user
            if not new_request.amount_revised:
                new_request.amount_revised = 0            
            new_request.event = Group.objects.filter(label__name = 'Events', name = event)[0]
            new_request.save()
            print "saved"
            return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))
    return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))


@needs_authentication
def finance(request,request_id=-1,department_str=None,portal=None,owner_name=None,edit=False):
    """
    Function called when finance portal is opened. Redirects to eventcoord if event coord logs in.
    Finance coords can edit any budget of any event. They can approve requests by events.
    """
    print portal
    success = False
    print request_id
    page_owner = get_page_owner (request, owner_name)
    user = request.user
    if (str(user) == str(page_owner)):
        allow_adding_request = True
    print user.get_profile().get_dept ()
    # Check if event coord
    if str(user.get_profile().get_dept ()) == "Events":
        return HttpResponseRedirect("events/")
    if department_str == None or department_str == "":
        return HttpResponseRedirect(str(user.get_profile().get_dept ()))
        
    if str(user.get_profile().get_dept ()) == "Finance":
        finance_coord = True
#        all_events_data = get_all_departments()
        Form = BudgetFormCoord
        all_events_data = get_all_events()
        all_department_data = get_all_departments()        

    else:
        Form = BudgetForm      
        finance_coord = False
    if finance_coord or str(user) == str(page_owner):
        editable = True
        allow_adding_request = True        
    finance_form = Form()
    if department_str:
        department_object = Group.objects.filter(label__name = 'Department',
                                                 name = department_str)
    if not department_str:
        department_object = Group.objects.filter(label__name = 'Department',
                                                 name = user.get_profile().get_dept ())
    user_department = department_object[0].name
    advance_portal_finance_data = get_all_eventsadvanceportal()
    self_requests = Budget_Department.objects.filter(department = department_object)
    sum_amount_a,sum_amount_b,sum_amount_r = calculate_sums(self_requests)    
    if request_id >= 0:
        request_to_edit = Budget_Department.objects.get (id = request_id)
        Edit = True
        finance_form = Form(initial={'particular':request_to_edit.particular, 'requirement_date':request_to_edit.requirement_date, 'amount_a':request_to_edit.amount_a, 'amount_b':request_to_edit.amount_b, 'amount_revised':request_to_edit.amount_revised, 'status':request_to_edit.status})
        if request.method == 'POST':        
            finance_form = Form(request.POST)
            if finance_form.is_valid():
                request_to_edit.particular = finance_form.cleaned_data['particular']
                request_to_edit.requirement_date = finance_form.cleaned_data['requirement_date']
                request_to_edit.amount_a = finance_form.cleaned_data['amount_a']
                request_to_edit.amount_b = finance_form.cleaned_data['amount_b']
                if finance_coord:
                    request_to_edit.amount_revised = finance_form.cleaned_data['amount_revised']
                    request_to_edit.status = finance_form.cleaned_data['status']                                                                                
                success = True
                request_to_edit.save()
#                return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))
                return HttpResponseRedirect("../")
        return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))
#            return redirect ('finance.views.finance', locals())

    if request.method == 'POST':
        finance_form = Form(request.POST)
        if finance_form.is_valid():
            new_request = finance_form.save (commit = False)
            success = True
            new_request.requester = user
            if not new_request.amount_revised:
                new_request.amount_revised = 0                        
            new_request.department = Group.objects.filter(
                label__name = 'Department',
                name = department_str)[0]
            new_request.save()
            return render_to_response('finance/budget_portal.html',locals(), context_instance = global_context (request))
    return render_to_response('finance/budget_portal.html',locals(),context_instance = global_context (request)) 


def deleterequestevent(request,owner_name=None,is_event=0,department_str="",request_id=-1):
    Budget_Event.objects.get (id = request_id).delete()
    return HttpResponseRedirect("../")

def deleterequestdept(request,owner_name=None,is_event=0,department_str="",request_id=-1):
    Budget_Department.objects.get (id = request_id).delete()
    return HttpResponseRedirect("../")
    
def financeedit(request,owner_name,request_id):
    page_owner = get_page_owner (request, owner_name)
    user = request.user
    curr_Request = Finance.objects.get(id = request_id)
    curr_subtask_form = SubTaskForm (request.POST, instance = curr_subtask)
    curr_subtask_form.save ()    
    return render_to_response('finance/edit_finance.html',locals())
