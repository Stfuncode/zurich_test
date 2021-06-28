from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Register)
admin.site.register(PolicyDetails)
admin.site.register(NomineeDetails)
admin.site.register(MSVR)
admin.site.register(MSVRChange)
admin.site.register(UserPolicy)
admin.site.register(ChangeRequest)