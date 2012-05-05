from django.conf.urls.defaults import *
from django.views.generic.simple import *

urlpatterns = patterns('users.views',
      (r'^$', 'handle_profile'),
      (r'^register/?(?P<dept_name>\w+)?/$', 'register_user'),
      # (r'^register_invite/?(\w+)?/?(\w+)?/?(\w+)?/$', 'register_invite'),
      (r'^invite/$', 'invite'),
      (r'^invite_inbulk/$', 'invite_inbulk'),
      (r'^profile/$', 'view_profile'),
      (r'^edit_profile/$', 'handle_profile'),
      (r'^js_test/$','js_test'),
      (r'^manage_circles/$', 'manage_circle'),
      (r'^manage_groups/$', 'manage_groups'),

)

urlpatterns +=patterns('',
      (r'^change_profile_pic/$', 'erp_test.dashboard.views.change_profile_pic'),
)

