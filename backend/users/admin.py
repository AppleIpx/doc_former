from django.contrib import admin
from .models import User
from django.contrib.admin import register


@register(User)
class UserAdmin(admin.ModelAdmin):
    fields = (
        # "pk",
        "is_staff",
        "first_name",
        "last_name",
        "patronymic",
        "username",
        "password",
        "first_password",
        "course",
        "direction_specialty",
        "group",
        "email",
        "faculty",
    )
    list_display = (
        "pk",
        "last_name",
        "first_name",
        "username",
        "first_password",
        "is_teacher",
        # "password",
    )

    ordering = ["last_name", ]
