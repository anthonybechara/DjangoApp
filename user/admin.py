from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from user.models import User


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    readonly_fields = ('created_date', 'modified_date', 'last_login', 'last_logout')
    list_display = (
        'username', 'email', 'phone_number', 'first_name', 'last_name', 'middle_name', 'is_online', 'is_active',
        'is_admin', 'is_superuser', 'last_login', 'last_logout')

    list_filter = ('is_active', 'is_admin')

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'middle_name', 'username', 'email', 'phone_number', 'password',
                       'gender', 'birth_date', 'photo', 'country', 'city', 'slug')
        }),
        ('Permissions', {
            'fields': ('is_online', 'is_active', 'is_admin', 'is_superuser', 'user_permissions')
        }),
        ('Dates', {
            'fields': ('created_date', 'modified_date', 'last_login', 'last_logout')
        }),
    )

    add_fieldsets = (
        (None,
         {'fields': (
             'first_name', 'last_name', 'middle_name', 'username', 'email', 'phone_number', 'password1', 'password2')}),
    )

    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')

    ordering = ('first_name',)

    filter_horizontal = ('user_permissions',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


admin.site.register(User, CustomUserAdmin)
# admin.site.unregister(Group)
