from django.conf.urls.defaults import *
from django.views.generic.simple import *
from django.contrib import admin
import views
# TODO
# Caution : Any non-matched url goes straight to display_portal and
# gives an error since a user of that name would not be found.
urlpatterns = patterns('finance.views',
                       (r'^$', 'finance'),
                       (r'^(?P<event>[a-zA-Z0-9 \-\.\(\)!&\']*)/1/process/$', 'process_advance_finance'),                       
                       (r'^events/(?P<event>[a-zA-Z0-9 \-\.\(\)!&\']*)/process/$', 'process_advance'),
                       
                       (r'^(?P<department>[a-zA-Z0-9 \-\.\(\)!&\']*)/(?P<is_event>[0-1])[/]*$', 'financecoord'),
                       (r'^events/(?P<event>[a-zA-Z0-9 \-\.\(\)!&\']*)[/]*$', 'eventcoord'),
                       (r'^events/(?P<department_str>[a-zA-Z0-9 \-\.\(\)!&\']*)/(?P<request_id>\d+)/delete[/]*$', 'deleterequestevent'),
                       (r'^(?P<department_str>[a-zA-Z0-9 \-\.\(\)!&\']*)/(?P<request_id>\d+)/delete[/]*$', 'deleterequestdept'),                
                       (r'^(?P<department_str>[a-zA-Z0-9 \-\.\(\)!&\']*)[/]*$', 'finance'),                       
                       (r'^(?P<department_str>[a-zA-Z0-9 \-\.\(\)!&\']*)/(?P<request_id>[0-9]+)[/]*$', 'finance'),
                       (r'^events/(?P<event>[a-zA-Z0-9 \-\.\(\)!&\']*)/(?P<request_id>\d+)[/]*$', 'eventcoord'),

                       
                       #      (r'^events/', 'eventcoord'),                                                                     
                       # (r'^(\w+)?$', 'display_portal'),
)
