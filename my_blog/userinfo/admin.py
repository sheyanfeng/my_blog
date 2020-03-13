# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import UserInfo
# from django.contrib.auth.models import User
# class ProfileInline(admin.StackedInline):
#     model = UserInfo
#     can_delete = False
#     verbose_name_plural = 'UserProfile'
# class UserAdmin(BaseUserAdmin):
#     inlines = (ProfileInline,)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# # Register your models here.

from django.contrib import admin
from .models import UserInfo

admin.site.register(UserInfo)