import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, teams, events, feedback, dtrace


@cache_page(settings.PAGE_CACHE_TIME)
def dash_dtrace(request):
    try:
        cursor = connections['dwh'].cursor()

        # Все мероприятия острова с факультетом
        cursor.execute(events.event_department_all)
        all_events_df = pd.DataFrame(dictfetchall(cursor))

        # Все мероприятия острова с записями
        cursor.execute(events.event_enrolls_all_aggr)
        event_enrolls_df = pd.DataFrame(dictfetchall(cursor))
        all_events_df = pd.merge(all_events_df, event_enrolls_df, on='event_uuid', how='left')
        print(all_events_df.shape)

        # Все мероприятия острова с обратной связью
        cursor.execute(feedback.event_feedback_rating_aggr)
        event_feedback_df = pd.DataFrame(dictfetchall(cursor))
        all_events_df = pd.merge(all_events_df, event_feedback_df, on='event_uuid', how='left')
        print(all_events_df.shape)

        # Все мероприятия остова с персональным цифровым следом
        cursor.execute(dtrace.event_material_aggr_all)
        event_dtrace = pd.DataFrame(dictfetchall(cursor))
        all_events_df = pd.merge(all_events_df, event_dtrace, on='event_uuid', how='left')
        print(all_events_df.shape)

        # Все ставки на аукционе
        cursor.execute(auction.auction_bets_all)
        event_bet_df = pd.DataFrame(dictfetchall(cursor))
        all_events_df = pd.merge(all_events_df, event_bet_df, on='event_uuid', how='left')
        print(all_events_df.shape)

        result = {}
        print(all_events_df.columns)

        event_day_df = all_events_df.groupby(pd.Grouper(key='endDT', freq='D')).agg(
            {'enrolls_count': 'sum', 'dtrace_user_count': 'sum', 'avg_score': 'mean', 'feedback_users_count': 'sum',
             'bets_count': 'sum'}).cumsum().reset_index()
        event_day_df["N"] = event_day_df.index
        result['event_day_enroll_data'] = event_day_df[["N", "enrolls_count"]].values.tolist()
        result['event_day_enroll_last'] = event_day_df['enrolls_count'].iloc[-1]
        event_day_df['drace_ratio'] = event_day_df['dtrace_user_count'] / event_day_df['enrolls_count']
        # result['event_day_dtrace_data'] = event_day_df[["N", "drace_ratio"]].values.tolist()
        result['event_day_dtrace_data'] = event_day_df[["N", "dtrace_user_count"]].values.tolist()
        result['event_day_dtrace_last'] = event_day_df['dtrace_user_count'].iloc[-1]

        result['event_day_feedback_data'] = event_day_df[["N", "feedback_users_count"]].values.tolist()
        result['event_day_feedback_last'] = event_day_df['feedback_users_count'].iloc[-1]
        result['event_day_bets_data'] = event_day_df[["N", "bets_count"]].values.tolist()
        result['event_day_bets_last'] = event_day_df['bets_count'].iloc[-1]
        event_day_df['endDT'] = event_day_df['endDT'].dt.strftime('%d.%m')
        result['event_day_chart_ticks'] = event_day_df[["N", "endDT"]].values.tolist()

        event_rating_df = all_events_df.groupby('event_uuid').agg(
            {'event_title': 'first', 'type_title': 'first', 'dep_title': 'first', 'startDT': 'first', 'endDT': 'first', 'enrolls_count': 'sum',
             'dtrace_user_count': 'sum', 'avg_score': 'mean',
             'feedback_users_count': 'sum',
             'bets_count': 'sum'}).reset_index()
        event_rating_df['rating'] = event_rating_df['dtrace_user_count'] / event_rating_df['enrolls_count']
        event_rating_df = event_rating_df.sort_values('avg_score', ascending=False)
        result['event_rating'] = event_rating_df.to_dict('record')

        print(all_events_df.shape)

    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/dtrace.html", {'result': result})


# @cache_page(settings.PAGE_CACHE_TIME)
def dash_dtrace_teams(request):
    result = {}
    try:
        cursor = connections['dwh'].cursor()

        # Все мероприятия острова с факультетом
        cursor.execute(events.event_enrolls_all)
        all_enrolls_df = pd.DataFrame(dictfetchall(cursor))
        print(all_enrolls_df.shape)

        # Все мероприятия острова с обратной связью
        cursor.execute(feedback.event_feedback_rating)
        event_feedback_df = pd.DataFrame(dictfetchall(cursor))
        all_enrolls_df = pd.merge(all_enrolls_df, event_feedback_df, on='user_event', how='left')
        print(all_enrolls_df.shape)

        # Все мероприятия остова с персональным цифровым следом
        cursor.execute(dtrace.event_material_all)
        event_dtrace = pd.DataFrame(dictfetchall(cursor))
        all_enrolls_df = pd.merge(all_enrolls_df, event_dtrace, on='user_event', how='left')
        print(all_enrolls_df.shape)

        # Все команды острова
        cursor.execute(teams.user_teams)
        teams_load_df = pd.DataFrame(dictfetchall(cursor))
        all_enrolls_df = pd.merge(all_enrolls_df, teams_load_df, on='leaderID', how='left')
        print(all_enrolls_df.shape)
        print(all_enrolls_df.columns)

        all_enrolls_df = all_enrolls_df.groupby('team_title').agg({'value': 'count', 'dtrace': 'count', 'event_uuid':'count'})
        all_enrolls_df['value_rating'] = all_enrolls_df['value']/all_enrolls_df['event_uuid']
        all_enrolls_df['dtrace_rating'] = all_enrolls_df['dtrace'] / all_enrolls_df['event_uuid']

        team_reflex_rating_df =  all_enrolls_df.sort_values('value_rating', ascending=False).reset_index()
        team_reflex_rating_df['N'] = team_reflex_rating_df.index + 1

        team_dtrace_rating_df = all_enrolls_df.sort_values('dtrace_rating', ascending=False).reset_index()
        team_dtrace_rating_df['N'] = team_dtrace_rating_df.index + 1

        result['team_reflex_rating'] = team_reflex_rating_df.to_dict('record')
        result['team_dtrace_rating'] = team_dtrace_rating_df.to_dict('record')
        print('dtrace_team')
    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/dtrace_team.html", {'result': result})
