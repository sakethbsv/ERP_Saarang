from django.conf.urls.defaults import *
from django.views.generic.simple import *


urlpatterns = patterns('erp_test.qms_barcode.views',
      (r'^register/', 'participant_register'),
      (r'^search/', 'search'),
      (r'^update/', 'participant_update'),
      (r'^login/','coord_barcode_login'),
      (r'^events/$','events_reg'),
      (r'^logout/$', 'logout'),
      (r'^events/(?P<event>\w+)/$','show_details'),
      (r'^help/','help_text'),
      (r'^register_college','college_registration'),
)

#urlpatterns += patterns('erp_test.qms_barcode.rss',
#      (r'showall/$', 'showupdates'),
#      (r'show/(?P<u_id>\d*)/$', 'showupdates'),
#      (r'edit/(?P<u_id>\d*)/$', 'addoreditupdates'),
#      (r'add/$', 'addoreditupdates'),
#      
#)

