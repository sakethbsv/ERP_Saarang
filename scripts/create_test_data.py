# Helper functions
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template.context import Context, RequestContext
from django.db.models import Q
from erp_test import settings
from erp_test.users.models import userprofile, DEP_CHOICES, Group, Label, College
from erp_test.tasks.models import Task, SubTask, DEFAULT_STATUS, TaskComment, SubTaskComment, Update, Tag, doc_label_list
from erp_test.qms_barcode import models
from erp_test.qms_barcode.models import Event
import random ,datetime
import csv

group_label_list = ['Department', 'Festival', 'Event','BarCodeEvent']
group_label_list_barcode = ['BarcodeEvent' , 'Participant Team']

from erp_test.qms_barcode.models import Event

def create_auth_group (auth_group_name):
    """
    Create a auth_group with auth_group_name, if it doesn't already exist.
    """
    try:
        new_auth_group = auth.models.Group.objects.get (name = auth_group_name)
    except:
        new_auth_group = auth.models.Group (name = auth_group_name)
        new_auth_group.save ()
        print 'Group %s created' %(auth_group_name)
    
def create_auth_groups ():
    """
    Create auth_groups Cores, Coords, and Vols (if they don't already exist).
    """
    auth_group_list = ['Cores', 'Coords', 'Vols', 'Super-Coords']
    for auth_group_name in auth_group_list:
        create_auth_group (auth_group_name)
        print 'Group %s created' %(auth_group_name)
    

def create_auth_groups_barcode ():
    """
	    This is for the barcode registration for shaastra
    """

    auth_group_list = ['QMS_Reg','Event_Reg','ppm_Reg']
    for auth_group_name in auth_group_list:
        create_auth_group (auth_group_name)
        print 'Group %s created' %(auth_group_name)
     
def create_labels (label_list):
    """
    Create different labels.
    """
  
    for label in label_list:
  	try:
  	     label = Label.objects.get(name = label)
	     print 'Label : %s already there' % (label)  	    
	except:
	     Label.objects.create (name = label)
             print 'Label : %s created' % (label)

def create_Shaastra ():
    """
    Create the highest level group - Shaastra!
    """
    try:
        top_level_group = Group.objects.get (label__name = 'Festival')
    except:
        top_level_group = Group ()
        top_level_group.label = Label.objects.get (name = 'Festival')
        top_level_group.name = 'Shaastra'
        top_level_group.save ()

def create_depts ():
    """
    Create all the departments with names as given DEP_CHOICES.
    """
    top_level_group = Group.objects.get (label__name = 'Festival')
    for name, description in DEP_CHOICES:
        try:
            dept = Group.objects.get (label__name = 'Department', name = name)
        except:
            new_dept = Group ()
            new_dept.label = Label.objects.get (name = 'Department')
            new_dept.name = name
            new_dept.parent = top_level_group
            new_dept.save ()
            print 'Department %s created' % (name)
        else:
            print 'Department %s exists' % (name)

def create_event_list(file_name = "Events.csv"):
    """
    	This create event list
    """
    event_label = Label.objects.get( name = 'BarcodeEvent')
    ifile  = open(file_name, "r")
    reader = csv.reader(ifile ,delimiter=',')
    for row in reader:
	print "Event created : " ,row[0]
	#Createing a gropu which has name as name of the event
	event_object = Event.objects.create(label = event_label )
	event_object.name  = row[0]
	event_object.save()
    ifile.close ()


def create_college_list(file_name = 'College_list.csv'):
    ifile  = open(file_name, "r")
    reader = csv.reader(ifile ,delimiter=',')
    
    for row in reader:
		try :
		    College_object = College()
		    College_object.name = row[0]
		    College_object.city = row[1]
		    College_object.state = row[2] 
		    College_object.save()        
		except:
			print "not saved"
		         
        
        
def add_user_to_dept (user, dept_name):
    """
    Add user to given department, if not already a member.
    """
    dept = Group.objects.get (label__name = 'Department', name = dept_name)
    
    if not user.group_set.filter (id = dept.id).exists ():
        dept.members.add (user);
    
def add_user_to_auth_group (user, auth_group_name):
    # Allow access to admin interface
    if auth_group_name == 'Cores':
        user.is_staff = True
    else:
        user.is_staff = False
    user.groups.add (auth.models.Group.objects.get (name = auth_group_name))
    user.save ()
    print '%s - now a member of Group %s' %(user, auth_group_name)
    
def create_user (department_name, auth_group_name, user_dict, profile_dict):
    """
    Create a User and fill his userprofile.

    Return user.
    """
    try:
        # In case, user already exists
        user = User.objects.get (username = user_dict['username'])
        print '%s - User exists' % (user_dict['username'])
    except:
        # If it's a new user
        # Note : create_user creates an instance and saves it in the database

        # Delivering keyword args in user_dict
        user = User.objects.create_user(**user_dict)
        print '%s - User created' %(user_dict['username'])

    try:
        curr_userprofile = user.get_profile ()
        print "%s - userprofile exists" %(user_dict['username'])
    except:
        # If userprofile doesn't exist (whether or not user is a new
        # one or old one), create it
        profile_dict['user'] = user
        curr_userprofile = userprofile (**profile_dict)
        curr_userprofile.save ()
        print "%s - userprofile created" %(user_dict['username'])
    add_user_to_dept (user, department_name)
    add_user_to_auth_group (user, auth_group_name)
    return user

def parse_user_info_list (info_list):
    """
    Parse given line into appropriate data and return a list of department_name, auth_group_name, and two dicts :
    user_dict - which contains user info
      - username
      - email
      - password
      
    profile_dict - which contains userprofile info
      - nickname
      - name
      - chennai_number
      - summer_number
      - summer_stay
      - hostel
      - room_no
    """
    department_name = info_list[0]
    auth_group_name = info_list[1]
    user_keys = ['username', 'email', 'password']
    profile_keys = ['nickname', 'name', 'chennai_number', 'summer_number',
                    'summer_stay', 'hostel', 'room_no']
    user_values = info_list[2:5]
    profile_values = info_list[5:]
    user_dict = dict (zip (user_keys, user_values))
    profile_dict = dict (zip (profile_keys, profile_values))
    return [department_name, auth_group_name, user_dict, profile_dict]

def create_users (users_file_name = 'users.txt'):
    """
    Get user details from users_file_name.
    Create users if they doesn't exist.
    """
    users_file = open (users_file_name, 'r')
    for line in users_file:
        # user_fields = line.split ()
        user_data_list = parse_user_info_list (line.split ())
        create_user (*user_data_list)
    users_file.close ()
    print 'All users created successfully.'

# def create_task (task_details, subtask_list = None):
#     """
    
#     Arguments:
#     - `task_details`:
#     - `subtask_list`:
#     """
#     task_keys = ["subject", "description", "creator", "deadline"]
#     subtask_keys = ["subject", "description", "creator", "deadline"]
    
def create_tasks (n = 5, partial_subtask = False):
    """
    Create n (= 5) Tasks (with 2 SubTasks each) for each Department's
    Core, with some Deadline. One SubTask is for the Core's
    Department. The other is for a random Department.

    If partial_subtask = True, mark both SubTasks for other
    Departments (at random), but don't assign to their Coords.
    """
    
    dept_names = [tup[0] for tup in DEP_CHOICES]
    if partial_subtask:
        num_other_tasks = 2
        task_subj_str = ' Test Task (Partial) '
        subtask_subj_str_same = ' Same Dept - Do this (Partial)'
        subtask_subj_str_other = ' Other Dept - Do this (Partial)'
    else:
        num_other_tasks = 1
        task_subj_str = ' Test Task '
        subtask_subj_str_same = ' Same Dept - Do this '
        subtask_subj_str_other = ' Other Dept - Do this '


    for name in dept_names:
        curr_dept = Group.objects.get (label__name = 'Department', name = name)
        # This Department's Core
        curr_core = User.objects.filter (groups__name = 'Cores', group__id = curr_dept.id)[0]
        curr_coord1 = User.objects.filter (groups__name = 'Coords', group__id = curr_dept.id)[0]
        curr_coord2 = User.objects.filter (groups__name = 'Coords', group__id = curr_dept.id)[1]
        print 'Tasks for ', curr_dept.name
        
	start_date = datetime.date.today().replace(day=1, month=8).toordinal()
	end_date = datetime.date.today().toordinal()

        for i in xrange (n):
            new_task = Task ()
            new_task.subject = name + task_subj_str + str (i)
            new_task.description = 'Gen Testing ' + str (i)
            new_task.creator = curr_core
            if(start_date > end_date):
                new_task.deadline =  datetime.date.fromordinal(random.randint(end_date,start_date))
            else:
                new_task.deadline =  datetime.date.fromordinal(random.randint(start_date, end_date))
            new_task.save () 

            if not partial_subtask:
                subtask1 = SubTask ()
                subtask1.subject = name + subtask_subj_str_same + str (i)
                subtask1.creator = curr_core

                if(start_date > end_date):
                    subtask1.deadline =  datetime.date.fromordinal(random.randint(end_date,start_date))
                else:
                    subtask1.deadline =  datetime.date.fromordinal(random.randint(start_date, end_date))
                subtask1.department = curr_dept
                subtask1.task = new_task
                # Seems the SubTask must exist before many to many
                # relations can be added
                subtask1.save ()
                subtask1.coords.add (curr_coord1)
                subtask1.coords.add (curr_coord2)
                subtask1.save ()

            for j in xrange (num_other_tasks):
                subtask2 = SubTask ()
                subtask2.creator = curr_core

                if(start_date > end_date):
                    subtask2.deadline =  datetime.date.fromordinal(random.randint(end_date,start_date))
                else:
                    subtask2.deadline =  datetime.date.fromordinal(random.randint(start_date, end_date))
                index = random.randint (0, 9)
                subtask2.department = Group.objects.get (label__name = 'Department', name = dept_names[index])
                subtask2.subject = subtask2.department.name + subtask_subj_str_other + str (i)
                subtask2.task = new_task
                # Seems the SubTask must exist before many to many
                # relations can be added
                subtask2.save ()
                if not partial_subtask:
                    # If not a partial subtask, assign to coords
                    coord_list = User.objects.filter (groups__name = 'Coords', group__id = subtask2.department.id)
                    subtask2.coords.add (coord_list[0])
                    subtask2.coords.add (coord_list[1])
                    subtask2.save ()
                print 'Task ', i, 'Created'


def finish_some_subtasks ():
    """
    Mark one complete SubTask in each Department as Done.
    """
    dept_names = [tup[0] for tup in DEP_CHOICES]
    print 'Subtasks marked as completed :'
    for name in dept_names:
        # The SubTask must not be a partial SubTask (for the sake of testing)
        try:
            curr_subtask = SubTask.objects.filter (~Q (coords = None), department__name = name)[0]
            curr_subtask.status = 'Completed'
            print curr_subtask
            curr_subtask.save ()
        except:
            pass

def create_comments ():
    """
    Create some comments for each Task, SubTask.
    """
    cores_list = User.objects.filter (groups__name = 'Cores')
    coords_list = User.objects.filter (groups__name = 'Coords')
    standard_test_comment = ' Testing 123'
    for core in cores_list:
        task_list = Task.objects.filter (creator = core)
        subtask_list = SubTask.objects.filter (department = core.get_profile ().get_dept ())
        comment_string = core.get_profile ().name + ' '
        for task in task_list:
            new_comment = TaskComment (comment_string = comment_string + 'Task' + standard_test_comment)
            new_comment.author = core
            new_comment.task = task
            new_comment.save ()
        for subtask in subtask_list:
            new_comment = SubTaskComment (comment_string = comment_string + 'SubTask' + standard_test_comment)
            new_comment.author = core
            new_comment.subtask = subtask
            new_comment.save ()
    print 'Core comments - Created'

    for coord in coords_list:
        # List of all SubTasks where coord is one of the Coords assigned
        subtask_list = SubTask.objects.filter (coords = coord)
        comment_string = coord.get_profile ().name + ' '
        for subtask in subtask_list:
            new_comment = SubTaskComment (comment_string = comment_string + 'SubTask' + standard_test_comment)
            new_comment.author = coord
            new_comment.subtask = subtask
            new_comment.save ()
    print 'Coord comments - Created'
def create_updates ():
    """
    Create some updates for each Coord.
    """
    coords_list = User.objects.filter (groups__name = 'Coords')
    for coord in coords_list:
        # List of all SubTasks where coord is one of the Coords assigned
        new_update = Update (comment_string = 'Hey This is Me ' + coord.get_profile ().name, author = coord)
        new_update.save ()
        new_update = Update (comment_string = 'Yo! This is Me again! ' + coord.get_profile ().name, author = coord)
        new_update.save ()
        new_update = Update (comment_string = 'Guess What? ' + coord.get_profile ().name, author = coord)
        new_update.save ()
    print 'Coord updates - Created'

# Create Core
# create_test_data.create_user ('Webops', 'Cores', {'username' : 'me09b001', 'email' : '', 'password' : 'password'}, {'nickname' : 'IBM', 'name' : 'Siddharth', 'chennai_number' : '9999999999', 'summer_number' : '9999999999', 'summer_stay' : 'Bangalore', 'hostel' : 'Godavari', 'room_no' : '420'})

# def create_tags (n = 3):
#     """
#     Create n gen tags.
#     """
#     for i in xrange (n):
#         obj, is_created = Tag.objects.get_or_create (name = 'Tag ' + str (i))
#         print 'Tag ', str (i), ' Created : ', is_created
    
def import_events_junta (csv_file = '../Coords-Limited (Shaastra 2011).csv'):
    """




    BIG TODO!!!

    USE NEW DEPARTMENT / GROUP FORMAT.







    Format :

    ['Division', 'Event', 'Name', 'e-Mail id', 'Cell. Ph. ', 'Nick', 'Roll Num', 'Room', 'Hostel', 'Google Group Link', 'Google group email id']

    Super-Coords are both Coords and Super-Coords.
    """
    ifile  = open(csv_file, "rb")
    reader = csv.reader(ifile)

    division_index = 0
    event_index = 1
    name_index = 2
    email_id_index = 3
    roll_no_index = 6

    user_list = []
    rejected_rows = []
    num_cores = 3
    num_super_coords = 2
    password = 'password'

    first = True

    # Read rows from file
    for row in reader:
        try:
            curr_division = row [division_index]
            curr_event = row [event_index]
            curr_name = row [name_index]
            curr_email = row [email_id_index]
            curr_roll_no = row [roll_no_index].upper ()
        except:
            # Reject invalid rows
            rejected_rows.append (row)
        else:
            if curr_roll_no == '':
                # Reject rows without Roll No
                rejected_rows.append (row)
            else:
                user_list.append ([curr_division, curr_event, curr_name, curr_email, curr_roll_no])

    ifile.close()

    roll_no_index = 4

    print 'Rejects : ', rejected_rows

    # Create the cores
    core_details = [['Event Cores'] + row [1:] for row in user_list [1:(1+num_cores)]]
    for core in core_details:
        create_user (department_name = 'Events', group_name = 'Cores',
                     user_dict = {'username' : core[roll_no_index],
                                  'password' : password,
                                  'email' : core[email_id_index]},
                     profile_dict = {'name' : core[name_index]})
    for row in core_details:
        event = Event.objects.all()
        core2 = User.objects.get (username = row[roll_no_index])
        print core2
        for item in event:
            item.coords.add (core2)
    print 'Accounts for Events Cores created.'
    # print core_details

    # Create the Super-Coords
    super_coord_details = [['Super-Coords'] + row [1:] for row in user_list [(num_cores + 1):(num_cores + num_super_coords + 1)]]
    for super_coord in super_coord_details:
        new_user = create_user (department_name = 'Events', group_name = 'Coords',
                     user_dict = {'username' : super_coord[roll_no_index],
                                  'password' : password,
                                  'email' : super_coord[email_id_index]},
                     profile_dict = {'name' : super_coord[name_index]})
        # Super-Coords are both Coords and Super-Coords
        add_user_to_auth_group (new_user, 'Super-Coords')
    for row in super_coord_details:
        event = Event.objects.filter (division = EventDivision.objects.get(name=row[1]))
        supercoord = User.objects.get (username = row[roll_no_index])
        for item in event:
            item.coords.add (supercoord)
        print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


        
    print 'Accounts for Events Super-Coords created.'
    print super_coord_details

    coord_details = user_list [(num_super_coords + num_cores + 1):]

    # Fill in some common details (which are skipped in the CSV file)
    # eg. Only the first Automania coord will have event as Automania.
    # The remaining Automania coords have empty Event field
    for i in xrange (len (coord_details)):
        if coord_details[i][0] == '':
            coord_details[i][0] = coord_details[i - 1][0]
        if coord_details[i][1] == '':
            coord_details[i][1] = coord_details[i - 1][1]

    # Create the coords
    for coord in coord_details:
        create_user (department_name = 'Events', group_name = 'Coords',
                     user_dict = {'username' : coord[roll_no_index],
                                  'password' : password,
                                  'email' : coord[email_id_index]},
                     profile_dict = {'name' : coord[name_index]})
    print 'Accounts for Events Coords created.'
    print 'Accounts successfully created.'

    rejects = []
    for row in rejected_rows:
        if row != []:
            rejects.append (row)
    
    if rejects:
        print 'Some user details have been rejected because of insufficient data. \nPlease check them.'
        print 'Rejected Entries :\n', '\n'.join ([' '.join (row) for row in rejects])

    # Create Event Divisions
    division_list = [row[division_index] for row in coord_details]
    division_list = list (set (division_list))
    print division_list
    for division in division_list:
        event_div = EventDivision.objects.get_or_create (name = division)
        print event_div

    # Create Events
    event_list = [(row[division_index], row[event_index]) for row in coord_details]
    for event in event_list:
        event = Event.objects.get_or_create (name = event[1], division = EventDivision.objects.get (name = event[0]))
        print event

    # Assign coords to each Event
    for row in coord_details:
        event = Event.objects.get (name = row[event_index])
        coord = User.objects.get (username = row[roll_no_index])
        event.coords.add (coord)
"""    
def create_event_list ():
    
    #Create a auth_group with auth_group_name, if it doesn't already exist.
    
    event_list = ['Puzzle','Hackfest' , 'Robotics' , 'Contraption','Hacking' ]    
    for field in event_list:
        try:
            new_event = Event.objects.get (name = field)
        except:
            new_event = Event.objects.create(name = field)
            new_event.save ()
"""
def replicate_authuser_mainsite(file_name = "mainsite_authuser.csv"):
    ifile  = open(file_name, "r")
    reader = csv.reader(ifile ,delimiter=';')
    
    auth_user_id_index	= 0
    username_index		= 1
    first_name_index	= 2
    last_name_index	= 3
    email_index		= 4
    i = 0
    for row in reader:
    	print i ,"  ", row[username_index]
    	i=i+1
    	try:
		authuser_object = MainSiteAuthUsers()
		authuser_object.auth_user_id = row[auth_user_id_index]
		authuser_object.username = row[username_index]
		authuser_object.first_name = row[first_name_index]
		authuser_object.last_name = row[last_name_index]
		authuser_object.email = row[email_index]
                authuser_object.save()		
        except ():
        	print "there was an error in the data in " ,row[username_index]

    ifile.close()
	
def replicate_userprofile_mainsite(file_name = "barcode_details.csv"):

    ifile  = open(file_name, "r")
    reader = csv.reader(ifile ,delimiter=';')
    
    model_id_index 	= 0
    user_id_index	= 1
    gender_index	= 2
    age_index		= 3
    branch_index	= 4
    mobile_no_index= 5
    college_roll_index = 6
    college_id_index = 7
    shaastra_id_index= 8
    i=0
#    print reader
    for  row in reader :
        print i 
        i=i+1
	userprofile_object = MainSiteUserProfile()
	userprofile_object.user_id = int(row[user_id_index])
	userprofile_object.gender = row[gender_index]
	userprofile_object.age = int(row[age_index])
	userprofile_object.branch = row[branch_index]
	userprofile_object.mobile_number = row[mobile_no_index]
	userprofile_object.college_roll = row[college_roll_index]
	userprofile_object.college_id = row[college_id_index]	
	try:
  	    userprofile_object.shaastra_id = row[shaastra_id_index]
  	except:
  	    userprofile_object.shaastra_id = "NoField"
	print row[shaastra_id_index]
	try:
 	    userprofile_object.save()
	except:
 	    print "There was an error while saving"
 	
    ifile.close()
    

def do_it_all ():

    create_labels (group_label_list)
    create_labels (doc_label_list)
    create_Shaastra ()
    create_auth_groups ()
    create_depts ()
    create_users (users_file_name = 'users.txt')
    create_tasks (n = 5, partial_subtask = False)
    create_tasks (n = 3, partial_subtask = True)
    finish_some_subtasks ()
    create_updates ()
    create_comments ()
    create_event_list()
    # create_tags ()
    
def do_it_barcode():
	
    create_labels (group_label_list)						#This creates label for coord , core etc
    create_labels (group_label_list_barcode) 		#This creates label for the registration group
    create_Shaastra ()    										#This creates the festival group , everything is taken from this group
    create_auth_groups ()										#Creates the groups core ,coord ...
    create_auth_groups_barcode ()						#Creates the groups for registration purpose
    create_depts ()												#Creates depts for the users who wil register
    create_users (users_file_name = 'users_barcode.txt')    #create the users , change the password and all here
    create_event_list()											#Creates the list of events in shaastra
    create_college_list()										#Creates college list
    
    """
    Yet to create the college list script
    and even event list script
    """
