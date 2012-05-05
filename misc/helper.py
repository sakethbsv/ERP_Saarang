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
from erp_test import settings
# Temporary workaround for the fact that I don't know whether / how to
# extend the User class with methods
def is_core (user):
    """
    Return True if user is a Core.
    """
    if user.groups.filter (name = 'Cores'):
        return True
    return False

def is_coord (user):
    """
    Return True if user is a Coord.
    """
    if user.groups.filter (name = 'Coords'):
        return True
    return False

def is_supercoord (user):
    """
    Return True if user is a Coord.
    """
    if user.groups.filter (name = 'Super-Coords'):
        return True
    return False

def get_page_owner (request, owner_name):
    """
    If owner_name is passed, return page owner, if he exists. If user
    with that name doesn't exist, return 'Invalid'.

    Else, return current user.

    Also, set the session variable for page_owner.
    """
    print 'Get Page Owner - owner_name : ', owner_name
    if owner_name == '' or owner_name is None:
        page_owner = request.user
    else:
        try:
            page_owner = User.objects.get (username = owner_name)
        except:
            return 'Invalid'
    # request.session['page_owner'] = page_owner
    # print request.session.items ()
    return page_owner

"""
this function creates the directory which will store infromation about the user
like his photos , documents

"""

def create_dir(file_name ,user_name , method=1):
    destdir_one=os.path.join(settings.MEDIA_ROOT,"upload_files")
    destdir=os.path.join(destdir_one,user_name)
    if not os.path.isdir(destdir):
        os.makedirs(destdir,0775)
    save_path=os.path.join(destdir,os.path.basename(file_name))
            
    destdir_one=os.path.join(settings.MEDIA_URL,"upload_files")
    destdir=os.path.join(destdir_one,user_name)
    print destdir , "is the destdir for the file"
    if not os.path.isdir(destdir):
        os.makedirs(destdir,0775)
    file_path=os.path.join(destdir,os.path.basename(file_name))
    
    return (save_path , file_path)



"""
this function writes the file
takes a file and saves it in recpective path


"""

def write_file(save_path ,f ,method=1):
    fout=open(save_path,'wb+')
    for chunk in f.chunks():
        fout.write(chunk)
    fout.close()
    
"""
helper function to mail junta
using it for invitation and forgot password thing

"""
def mail_coord(hyperlink ,mail_header ,name ,template,mail , password=""):
    mail_template=get_template(template)
    salt = sha.new(str(random.random())).hexdigest()[:5]
    activation_key = sha.new(salt+name).hexdigest()
    body=mail_template.render(Context({'coordname':name,
                                                   'SITE_URL':hyperlink,
                                                   'activationkey':activation_key,
                                                   'new_password':password
                                                   }))
    send_mail(mail_header,body,'noreply@shaastra.org',mail,fail_silently=False)
    success_message="mail sent"
    return success_message

def give_photo_array():
    pic_per_row=6;
    try:
        photo_list=userphoto.objects.filter()    
        num =photo_list.count()
	test_data=[[ {'photo':[] ,'variable':-1} for x in xrange(pic_per_row)] for y in xrange(num/pic_per_row+1)]
	for index ,photos in enumerate(photo_list):
	    test_data[index/pic_per_row][index%pic_per_row]['photo']=photos
	    test_data[index/pic_per_row][index%pic_per_row]['variable']=index
	    
	return test_data
    except:
        print "some serious probkem in helpers.py , profile_pic function"

def ensure_dir_exists (dir_name):
    """
    Create directory dir_name if it doesn't exist and return 'New'.
    Else, return 'Existing Dir'.
    """
    if not os.path.isdir (dir_name):
        os.makedirs(dir_name, 0775)
        return 'New Dir'
    return 'Existing Dir'
    
def get_file_path (instance, filename):
    """
    Get file path for an instance of a (Task/SubTask) Document.
    """
    file_path = os.path.join (settings.MEDIA_ROOT, 'upload_files', instance.uploader.username, filename)
    print ensure_dir_exists (os.path.dirname (file_path))
    return os.path.join ('upload_files', instance.uploader.username, filename)

def delete_this_file (file_path):
    """
    Delete file at file_path.
    """
    if os.path.isfile (str (file_path)):
        os.remove (str (file_path))
        print 'File at ', file_path, ' deleted.'
    else:
        print 'File not found.'
    
    
    


def send_mail_curr_info (request, subject = 'Test for Sessions'):
    try:
        user = request.user
    except:
        user = None
    session = request.session.items ()
    cookies = request.COOKIES
    message = subject + '\nrequest.user : ' + str (user) + '\nsession : ' + str (session) + '\nCookies : ' + str (cookies)
    if settings.SITE_URL == 'http://127.0.0.1:8000/erp_test':
        # print message
        pass
    else:
        # send_mail ('Debugging for Sessions', message, 'noreply@shaastra.org', ['gohanpra@gmail.com'])
        pass
