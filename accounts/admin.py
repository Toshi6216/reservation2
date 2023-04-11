from django.contrib import admin
from .models import CustomUser, StaffUser, MemberUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'nickname')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(StaffUser)
admin.site.register(MemberUser)
#admin.site.register(UserType)

#  first_name = models.CharField('名', max_length=150)
#     last_name = models.CharField('姓', max_length=150)
#     nickname = models.CharField('ニックネーム', max_length=150,  null=True, blank=True)
#     active = models.BooleanField(default=True)
#     staff = models.BooleanField(default=False) #staffかどうか
#     admin = models.BooleanField(default=False) 
