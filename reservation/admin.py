from django.contrib import admin
from .models import *

class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group_name')

class EventAdmin(admin.ModelAdmin):
    list_display = ('pk','event_title', 'group', 'event_date', 'start_time', 'end_time')

class ApplyingMemberAdmin(admin.ModelAdmin):
    list_display = ('pk', 'member', 'group', 'applying')

class ApplyingStaffAdmin(admin.ModelAdmin):
    list_display = ('pk', 'staff', 'group', 'applying')

class ApprovedMemberAdmin(admin.ModelAdmin):
    list_display = ('pk', 'member', 'group', 'approved')

class ApprovedStaffAdmin(admin.ModelAdmin):
    list_display = ('pk', 'staff', 'group', 'approved',)

class JoinAdmin(admin.ModelAdmin):
    list_display = ('join_name', 'join_event', 'join')

admin.site.register(Group, GroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(ApplyingMember, ApplyingMemberAdmin)
admin.site.register(ApplyingStaff, ApplyingStaffAdmin)
admin.site.register(ApprovedMember, ApprovedMemberAdmin)
admin.site.register(ApprovedStaff, ApprovedStaffAdmin)
admin.site.register(Join, JoinAdmin)
