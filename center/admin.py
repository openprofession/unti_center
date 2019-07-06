from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from center.models import User
from . import models


def reg_admin_model(model):
    def _proxy(model_admin):
        admin.site.register(model, model_admin)
        return model_admin
    return _proxy


admin.site.register(User, UserAdmin)

@reg_admin_model(models.Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'public',
        'active',
        'url',
        'priority'
    )
    ordering = (
        'priority',
    )


@reg_admin_model(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'public',
        'active',
        'priority'
    )
    ordering = (
        'priority',
    )
