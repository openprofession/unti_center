import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events, sport


# @cache_page(settings.PAGE_CACHE_TIME)
def dash_timetable(request):
    result = {}
    try:
        cursor = connections['dwh'].cursor()
        if hasattr(request.user, 'leader_id'):
            print(request.user.leader_id)
            cursor.execute(events.timetable_by_leader.format(request.user.leader_id))
            events_df = pd.DataFrame(dictfetchall(cursor))
            events_df = events_df.sort_values('startDT', ascending=True)
            events_df['startDT'] = pd.to_datetime(events_df['startDT'])
            events_df['endDT'] = pd.to_datetime(events_df['endDT'])
            events_df['start'] = events_df['startDT'].dt
            events_df['start_h'] = events_df['startDT'].dt.hour + 3
            events_df['start_m'] = events_df['startDT'].dt.minute
            events_df['end_h'] = events_df['endDT'].dt.hour + 3
            events_df['end_m'] = events_df['endDT'].dt.minute
            result['events'] = events_df.to_dict('record')
            print(events_df.columns)
            print(events_df.shape)
            print(events_df.to_csv())
    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/timetable.html", {'result': result})
