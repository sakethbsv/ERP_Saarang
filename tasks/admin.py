from django.contrib import admin
from erp_test.tasks.models import *

admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(TaskComment)
admin.site.register(SubTaskComment)
