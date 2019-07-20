import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events, sport, teams


@cache_page(settings.PAGE_CACHE_TIME)
def dash_sport_rating(request):
    result = {}
    try:
        cursor = connections['dwh'].cursor()

        cursor.execute(sport.sport_enrolls_all)
        sport_enrolls_df = pd.DataFrame(dictfetchall(cursor))

        cursor.execute(sport.sport_attendance_all)
        sport_attendance_df = pd.DataFrame(dictfetchall(cursor))

        # print(sport_enrolls_df.shape)
        # print(sport_attendance_df.shape)
        cursor.execute(teams.user_teams)
        teams_load_df = pd.DataFrame(dictfetchall(cursor))

        cursor.execute(teams.team_count)
        teams_count_df = pd.DataFrame(dictfetchall(cursor))

        sport_enrolls_df = pd.merge(sport_enrolls_df, teams_load_df, on='leaderID', how='left')
        sport_enrolls_df = pd.merge(sport_enrolls_df, teams_count_df, on='team_id', how='left')
        sport_enrolls_df = pd.merge(sport_enrolls_df, sport_attendance_df, on='event_user', how='outer')

        print(sport_enrolls_df.columns)
        # print(sport_enrolls_df.shape)
        # sport_enrolls_df.to_clipboard()
        sport_enrolls_df['date'] = pd.to_datetime(sport_enrolls_df['eventDT'])

        enrolls_line_df = sport_enrolls_df.groupby(pd.Grouper(key='date', freq='D')).agg({'event_user': 'count', 'value': 'count'}).reset_index()

        team_line_df = sport_enrolls_df.groupby('team_title').agg({'event_user': 'count', 'value': 'count', 'team_users': 'first'}).reset_index()

        #result['enrolls_line'] =

    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/sport_result.html", {'result': result})
