from django.contrib.auth.models import User
import sha,random,datetime,calendar
from django.core.mail import send_mail,EmailMessage,SMTPConnection
from django.template.loader import get_template
from django.template.context import Context, RequestContext
import os
from django.conf import settings
from erp_test.users.models import userphoto
#from erp_test.tasks.models import SubTask
from erp_test.tasks.models import *


def calendar_right_bottom(request,page_owner,Task):

    """
    this is used to get the details of the users tasks,subtasks
    in calendar format , will be displayed on the right bottom of pages   
    
    """
    now = datetime.datetime.now()
    today=now.day
    year=now.year
    month=now.month
    month_arr=["Jan" ,"Feb" ,"Mar" ,"April" ,"May" ,"Jun" ,"Jul" ,"Aug" ,"Sept","Oct","Nov","Dec"]
    month_name=month_arr[month-3:month+2]
    #the calander object
    
    mycalendar_b2 = calendar.monthcalendar(year ,month-1)
    mycalendar_b1= calendar.monthcalendar(year ,month-2)
    mycalendar = calendar.monthcalendar(year ,month)
    mycalendar_year = calendar.calendar(year)
    mycalendar_f1 = calendar.monthcalendar(year ,month+1)
    if(month ==11):
        mycalendar_f2 = calendar.monthcalendar(year+1 ,1)
    else:
        mycalendar_f2 = calendar.monthcalendar(year ,month+2)
    
    if is_core(page_owner):
        user_tasks=Task.objects.filter(creator = page_owner)
    else:	
        user_tasks=SubTask.objects.filter(coords=page_owner)  
    
    first_week_day=weekday(mycalendar[0])#gives the gap between weekday number of 1st
    calendar_data_b2=[[{'subtask':[],'date':0} for x in range(0,7)]for y in range(0,6)]
    calendar_data_b1=[[{'subtask':[],'date':0} for x in range(0,7)]for y in range(0,6)]
    calendar_data=[[[{'subtask':[],'date':0} for x in range(0,7)]for y in range(0,6)]for z in xrange(0,5)]
    calendar_data_f1=[[{'subtask':[],'date':0} for x in range(0,7)]for y in range(0,6)]
    calendar_data_f2=[[{'subtask':[],'date':0} for x in range(0,7)]for y in range(0,6)]
    
    
    initialize_calendar_data(mycalendar ,calendar_data[2])	
    initialize_calendar_data(mycalendar_f1 ,calendar_data[3])	
    initialize_calendar_data(mycalendar_f2,calendar_data[4])	
    initialize_calendar_data(mycalendar_b1 ,calendar_data[0])	
    initialize_calendar_data(mycalendar_b2 ,calendar_data[1])	
    #adding subtask in complete_data
    for index ,sub in enumerate(user_tasks):
        try:
            pos_to_task=int(sub.deadline.day+first_week_day)-1
	    calendar_data[sub.deadline.month-month+2][pos_to_task/7][pos_to_task%7]['subtask'].append(sub)
	    
	except: 
               print"some of the tasks dont have date in the given three months ,but mostly there is a cup in the function check it"
    return calendar_data, now ,month_name
    
    
    
def weekday(arr):
    for data in range(0,6):
        if arr[data]:
            return data
    return 0       
    
    
def initialize_calendar_data(mycalendar ,calendar_data):
    for index1 ,row in enumerate(mycalendar):
        for index2 ,col in enumerate(row):
    	    calendar_data[index1][index2]['date']=col
    

