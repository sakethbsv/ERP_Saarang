from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import password_reset
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('home.views',
      (r'^$', 'home'),
      (r'^login/$', 'login'),
      (r'^forgot_password/$', 'password_forgot'),
      (r'^change_password/(?P<activation_key>\w+)/(?P<username>\w+)$', 'change_password'),
      #(r'^login/forgot/$', 'forgot_password'),
      #(r'^login/forgot/(?P<u_name>[a-zA-Z0-9_.-]+)/(?P<new_pass>[\w]+)/?$', 'reset_password'),

      (r'^reset_password/$', 'reset_password'),
      (r'^reset_password/done/$', direct_to_template, { 'template' : 'home/reset_password_done.html', }),
      (r'^logout/$', 'logout'),
      #(r'^check/$','check'),
      #(r'^deadlines/$','deadlines')
      #(r'^registered/$','registered'),
)

