from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

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


@reg_admin_model(models.ExportFilter)
class ExportFilterAdmin(admin.ModelAdmin):
    list_display = (
        'name_column',
        'name_url_arg',
        'name_verbose',
        # 'description',
        'operator',
        'is_choices',
        'is_disabled',
        'data_type',
    )


@reg_admin_model(models.DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        # 'description',
        # 'sql',
        # 'filters',
        'is_disabled',
        'result_file_name',
    )



