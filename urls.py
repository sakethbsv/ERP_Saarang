from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from erp_test.tasks.views import *
from erp_test.users.views import *
from erp_test.home.views import *
from erp_test.finance.views import *
from erp_test.qms_barcode.views import *



# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^erp_test/$', include('qms_barcode.urls')),
    (r'^erp_test/home/',include('home.urls')),
    (r'^erp_test/users/', include('users.urls')),
    (r'^erp_test/participant/', include('qms_barcode.urls')),
    (r'^erp_test/(?P<owner_name>\w+)/finance/', include('finance.urls')),                       
    #(r'^dashboard/',include('dashboard.urls')),	
    # Make the above 2 URLConfs look like these 2 below
    (r'^erp_test/(?P<owner_name>\w+)/users/', include('users.urls')),
    (r'^erp_test/(?P<owner_name>\w+)/dashboard/',include('dashboard.urls')),	
    (r'^erp_test/(?P<owner_name>\w+)/', include('tasks.urls')),
    #(r'^now/sign.html$', sign_in, ),
    # Examples:
    # url(r'^$', 'erp_test.views.home', name='home'),
    # url(r'^', include('foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'erp_test/^admin/', include(admin.site.urls)),
)

