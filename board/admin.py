from django.contrib import admin

from .models import *

admin.site.register(Board)
admin.site.register(TestRecord)
admin.site.register(TestSchedule)
admin.site.register(ErrorRecord)