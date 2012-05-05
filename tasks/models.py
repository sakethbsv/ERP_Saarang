from django.db import models
from django.contrib.auth.models import User
from erp_test import settings
from erp_test.users.models import Group, Label
from erp_test.misc.helper import is_core, is_coord, get_page_owner, get_file_path
import os

# Create your models here.
#The choices may be cup level but if any thing better pls do change.
STAT_CHOICES= (
	('Open','Open'),
	('Completed','Completed'),
	('Late','Overdue'),
	('Almost Completed','Almost'),
)

DEFAULT_STATUS = 'Open'

doc_label_list = [ 'TeamDetails',
                   'DepartmentManual',
                   'MinutesOfMeeting',
                   'DepartmentPolicies',
                   'DepartmentReport',
                   'PreviousYearFeedback',
                   'OtherDocuments']

doc_heading_list = [ 'Team Details',
                     'Department Manual',
                     'Minutes Of Meeting',
                     'Department Policies',
                     'Department Report',
                     'Previous Year Feedback',
                     'Other Documents']

class AbstractBaseTask(models.Model):
    """
    Abstract Base Class for Task, SubTask.

    TODO:
    * File upload
    * Draft saving
    * QMS Manager for the Task
    """
    subject       = models.CharField(max_length=100 , null=True)
    description   = models.TextField(null=True , blank=True)
    creator       = models.ForeignKey(User, related_name = '%(app_label)s_%(class)s_creator')
    creation_date = models.DateTimeField (auto_now = True, editable = False)
    deadline      = models.DateField(null=True , blank=True)
    status        = models.CharField(max_length=20, choices=STAT_CHOICES,default = DEFAULT_STATUS)	

    
    class Meta:
        abstract = True
        
class Task(AbstractBaseTask):

    """
    Task Model

    Note : The department where the Task originated is understood from
    the Creator's department. As of now, only Cores can create Tasks.

    A Task mainly consists of SubTasks which are created and assigned by the respective Cores of each department.
    """
    # tags = models.ManyToManyField (Tag, blank = True)
    def is_owner (self, user):
        """
        user is the owner of the current Task if
        - user is a Core in the Task's department
        """
        print 'User Dept : ', user.get_profile ().get_dept ().name
        print 'Is Core : ', is_core (user)
        print 'Task Dept : ', self.creator.get_profile ().get_dept ().name
        return user.get_profile ().get_dept () == self.creator.get_profile ().get_dept () and is_core (user)

    def __str__(self):
        return str (self.subject)

    class Admin:
        pass

class SubTask(AbstractBaseTask):
    """
    SubTask Model

    As of now, SubTasks can be created mainly in two places :

    * When a Core breaks Tasks down into SubTasks and assigns some of
      them to Coords in his own department and/or delegates a SubTask
      to another Department (whose core has to then assign that
      SubTask to that department's coords, possibly creating more
      SubTasks as required)

    * When a Coord creates goals with deadlines for himself (these are
      called SubTasks but will actually be shown in his Timeline and
      handled differently from SubTasks that have been assigned to him
      by Cores)
    """
    coords = models.ManyToManyField (User, blank = True)
    department = models.ForeignKey (Group)
    task = models.ForeignKey (Task)

    def is_owner (self, user):
        """
        user is the owner of the current SubTask if
        - user is a Core in the department which created the Task
          which SubTask is related to
        - user is a Core in the department to which SubTask is assigned
        """
        print 'User Dept : ', user.get_profile ().get_dept ()
        print 'Is Core : ', is_core (user)
        print 'Task Dept : ', self.task.creator.get_profile ().get_dept ()
        print 'SubTask Dept : ', self.department
        user_dept = user.get_profile().get_dept ()
        return is_core (user) and (
            (user_dept == self.task.creator.get_profile ().get_dept ()) or
            (user_dept == self.department))

    def is_assignee (self, user):
        """
        Return True if user is a Coord who has been assigned this subtask.
        """
        print 'User Dept : ', user.get_profile ().get_dept ()
        print 'Is Coord : ', is_coord (user)
        user_dept = user.get_profile().get_dept ()
        return is_coord (user) and (self.coords.filter (id = user.id).exists ())

    def __str__(self):
        return str (self.subject)

    class Admin:
        pass

class Tag (models.Model):
    name = models.CharField (max_length = 100, blank = True)
    task = models.ManyToManyField (Task, blank = True)
    
    def __str__(self):
        return self.name

class AbstractComment (models.Model):
    """
    Abstract Base Class to store a comment.

    Timestamp helps to order comments. It is generated automatically.
    Author can be used to select particular comments based on the author.
    """
    author = models.ForeignKey (User, related_name = '%(app_label)s_%(class)s_author')
    comment_string = models.TextField ()
    time_stamp = models.DateTimeField (auto_now = True, editable = False)

    class Meta:
        abstract = True
        ordering = ['time_stamp']

class TaskComment(AbstractComment):
    """
    Comment written for a Task.
    """
    task = models.ForeignKey (Task)

    def __str__(self):
        return '%s %s' %(self.task.subject, self.id)
    class Admin:
        pass
        
        
class SubTaskComment(AbstractComment):
    """
    Comment written for a SubTask
    """
    subtask = models.ForeignKey (SubTask)

    def __str__(self):
        return '%s %s' %(self.subtask.subject, self.id)
    class Admin:
        pass
    
class Update (AbstractComment):
    """
    Used by Coord to send updates to a Core
    """
    class Admin:
        pass

class Document (models.Model):
    """
    Class for file upload.
    """
    document = models.FileField (upload_to = get_file_path, blank = True)
    uploader = models.ForeignKey (User)
    upload_date = models.DateTimeField (auto_now = True, editable = False)
    description = models.CharField(max_length = 100, blank = True)
    label = models.ForeignKey (Label, blank = True, null = True)

    def __str__(self):
        if self.document is not None:
            return '%s' % (os.path.basename (self.document.name))
        else:
            return 'Empty Doc'

    def get_document_heading (self):
        """
        Return heading for the Document.
        """
        heading_dict = dict (zip (doc_label_list, doc_heading_list))
        if self.label is not None:
            return heading_dict[self.label.name]
        else:
            return ''
        
    def get_google_docs_path (self):
        """
        Return link to Google Docs page for viewing current Document.
        """
        return ("http://docs.google.com/viewer?url=" +
                settings.MEDIA_URL + self.document.name)

# NOTE : Later, remove TaskDocument and SubTaskDocument models and
# simply have 'Task' and 'SubTask' as Labels

class TaskDocument (Document):
    """
    File upload for a Task.
    """
    task = models.ForeignKey (Task)
        
    # def __str__(self):
    #     return '%s' % (os.path.basename (self.document.name))


class SubTaskDocument (Document):
    """
    File upload for a SubTask.
    """
    subtask = models.ForeignKey (SubTask)
        
    # def __str__(self):
    #     return '%s' % (os.path.basename (self.document.name))


