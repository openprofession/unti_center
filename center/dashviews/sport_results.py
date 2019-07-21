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

        event_rating_df = sport_enrolls_df
        print(sport_enrolls_df.columns)
        # print(sport_enrolls_df.shape)
        # sport_enrolls_df.to_clipboard()
        sport_enrolls_df['date'] = pd.to_datetime(sport_enrolls_df['eventDT'])

        ang_users = sport_enrolls_df.groupby('leaderID_x').agg({'team_title': 'first', 'value': 'count'}).reset_index()
        ang_users.rename(columns={'value': 'ang'}, inplace=True)
        ang_users = ang_users.query('ang > 4')
        ang_teams = ang_users.groupby('team_title').agg({'ang': 'count'})


        enrolls_line_df = sport_enrolls_df.groupby(pd.Grouper(key='date', freq='D')).agg({'event_user': 'count', 'value': 'count'}).reset_index()
        enrolls_line_df['N'] = enrolls_line_df.index + 1
        enrolls_line_df['date'] = enrolls_line_df['date'].dt.strftime('%d.%m')
        team_line_df = sport_enrolls_df.groupby('team_title').agg({'event_user': 'count', 'value': 'count', 'leaderID_x': 'nunique', 'team_users': 'first'}).reset_index()
        team_line_df = pd.merge(team_line_df, ang_teams, on='team_title', how='left')
        team_line_df['rating'] = team_line_df['ang'] / team_line_df['team_users']
        team_line_df = team_line_df.sort_values(by='rating', ascending=False).reset_index()
        team_line_df['N'] = team_line_df.index + 1

        event_rating_df['title'] = event_rating_df['title'].str.rstrip()
        event_rating_df = event_rating_df.groupby('event_id_x').agg({'event_user': 'count', 'value': 'count', 'sizeMax': 'first', 'title': 'first'}).reset_index()
        event_rating_df = event_rating_df.groupby('title').agg({'event_user': 'sum', 'value': 'sum', 'sizeMax': 'sum'}).reset_index()
        event_rating_df['rating'] = event_rating_df['value'] / event_rating_df['sizeMax']
        event_rating_df = event_rating_df.sort_values(by='value', ascending=False).reset_index()
        event_rating_df['N'] = event_rating_df.index + 1

        # event_rating_df.to_clipboard()

        result['enrolls_line'] = enrolls_line_df[['N', 'event_user']].values.tolist()
        result['attendance_line'] = enrolls_line_df[['N', 'value']].values.tolist()
        enrolls_line_df['N'] = enrolls_line_df['N'] - 1
        result['time_line'] = enrolls_line_df[['N', 'date']].values.tolist()
        result['sum_enroll'] = enrolls_line_df['event_user'].sum()
        result['sum_attendance'] = enrolls_line_df['value'].sum()

        result['team_rating'] = team_line_df.to_dict('record')
        result['event_rating'] = event_rating_df.to_dict('record')

        result['ang_teams'] = team_line_df.query('ang/team_users > 0.55')['N'].count()
    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/sport_result.html", {'result': result})
