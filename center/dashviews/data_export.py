import pandas as pd
from django.db import connections
from django.template.defaultfilters import slugify

from center.dash_views import dictfetchall
from io import BytesIO

from django import forms

from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from .. import models
from django.http import HttpRequest
from pandas.api.types import is_datetime64_any_dtype


# https://github.com/wq/django-rest-pandas

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html
# https://stackoverflow.com/questions/28058563/write-to-stringio-object-using-pandas-excelwriter
# https://stackoverflow.com/questions/35267585/django-pandas-to-http-response-download-file


# https://stackoverflow.com/questions/42722018/pandas-localize-and-convert-datetime-column-instead-of-the-datetimeindex
# https://stackoverflow.com/questions/13994594/how-to-add-timezone-into-a-naive-datetime-instance-in-python

def exports_list(request, export_pk=None):
    exports = models.DataExport.objects.filter(
        is_disabled=False
    ).all()
    selected_export = exports.filter(pk=export_pk).first()

    # -------------------------------------------------------------------- #
    # df_cards
    #      first_name         incident_dt  ...     status    type
    # 0          Егор 2019-07-10 21:00:00  ...     issued     red
    # 1          Егор 2019-07-09 21:00:00  ...     issued  yellow
    #
    # from pandas.api.types import is_string_dtype
    # df_cards.columns
    # is_string_dtype(df_cards['last_name'].dtype)
    # df_cards.type.unique()  # ['red', 'yellow', 'green']
    # df_cards.type.value_counts()  # green 671, red 290, yellow 1
    # -------------------------------------------------------------------- #
    form = None
    if selected_export:

        def _choices_callback(name_column):
            df = _get_df(request, selected_export)
            assert isinstance(df, pd.DataFrame)
            values = getattr(df, name_column).unique()
            return list(zip(values, values))
        #

        FilterForm = selected_export.get_form_cls(_choices_callback)
        form = FilterForm()
        #
        if request.method == 'POST':
            form = FilterForm(request.POST)
            if form.is_valid():
                return _export(request, selected_export, form)
    #   #   #
    # -------------------------------------------------------------------- #

    return render(request, "data_export.html", {
        'exports':          exports,
        'selected_export':  selected_export,
        'form':             form,
    })
    #


def _get_df(request, export):
    df = getattr(request, '_dwh_result_data', None)
    if df is None:
        cursor = connections['dwh'].cursor()
        cunt_records = cursor.execute(export.sql)
        data = dictfetchall(cursor)
        df = pd.DataFrame(data)
        setattr(request, '_dwh_result_data', df)
    #

    return df


def _export(request, export, form):
    assert isinstance(request, HttpRequest)
    assert isinstance(export, models.DataExport)
    assert isinstance(form, forms.Form)
    # -------------------------------------------------------------------- #
    tz = timezone.get_current_timezone()
    date_export = timezone.localtime(timezone.now())

    mem_file = BytesIO()
    writer = pd.ExcelWriter(mem_file, engine='xlsxwriter')
    # -------------------------------------------------------------------- #

    # -------------------------------------------------------------------- #
    df = _get_df(request, export)
    assert isinstance(df, pd.DataFrame)

    # >_ set timezone
    for column in df.columns:
        if not is_datetime64_any_dtype(getattr(df, column).dtype):
            continue
        #
        df[column] = pd.to_datetime(
                df[column]
        ).dt.tz_localize(
            'UTC'  # default in db must be UTC
        ).dt.tz_convert(
           tz  # convert to user timezone
        )
    #

    # - - -    - - -    - - -
    # >_ apply filters
    filters = form.cleaned_data
    for data_filter in export.get_filters():
        value = filters.get(data_filter.name_url_arg, None)
        if not value:
            continue
        #
        if value == models.ExportFilter.CHOICE_ANY:
            continue
        #
        # https://docs.python.org/3/library/operator.html
        # https://habr.com/ru/post/186608/
        df = df[getattr(getattr(df, data_filter.name_column), {
            models.ExportFilter.OPERATOR_EQUAL:             '__eq__',
            models.ExportFilter.OPERATOR_NOT_EQUAL:         '__ne__',

            models.ExportFilter.OPERATOR_GREATER_THEN:      '__gt__',
            models.ExportFilter.OPERATOR_LESS_THEN:         '__lt__',

            models.ExportFilter.OPERATOR_GREATER_OR_EQUAL:  '__ge__',
            models.ExportFilter.OPERATOR_LESS_OR_EQUAL:     '__le__',
        }[data_filter.operator])(value)]
    #   #
    # - - -    - - -    - - -

    # >_ remove tz info fro data - for save to excel
    for column in df.columns:
        if not is_datetime64_any_dtype(getattr(df, column).dtype):
            continue
        #
        df[column] = pd.to_datetime(
            df[column]
        ).apply(lambda x: x.replace(tzinfo=None))
    #
    df.to_excel(writer, "cards")
    # -------------------------------------------------------------------- #

    # -------------------------------------------------------------------- #
    writer.save()
    mem_file.seek(0)
    dump = mem_file.read()
    response = HttpResponse(
        dump,
        content_type='application'
                     '/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # set the file name in the Content-Disposition header
    response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(
        slugify('{}_{}_{}'.format(
            export.result_file_name,
            date_export.strftime('%Y-%m-%d_%H-%M_%Z'),
            len(df)
        ))
    )
    return response
