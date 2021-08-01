from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile

# Register your models here
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'password', 'last_login', 'date_joined', 'is_active')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()





admin.site.register(
    Account,
    AccountAdmin
)


admin.site.register(
    UserProfile,
)