from django.contrib import admin
from .models import Device, Usergroup, User

admin.site.register(Device)
#admin.site.register(Dataviews)
admin.site.register(Usergroup)
admin.site.register(User)

#先用这个看了一下多对多关系长什么样子，可以用，不过最后还是要弃掉
# Register your models here.
