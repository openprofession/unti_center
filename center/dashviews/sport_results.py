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

        cursor.execute(teams.user_teams)
        teams_load_df = pd.DataFrame(dictfetchall(cursor))

        sport_enrolls_df = pd.merge(sport_enrolls_df, teams_load_df, on='leaderID', how='left')
        print(sport_enrolls_df.columns)
        print(sport_enrolls_df.shape)
    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/sport_result.html", {'result': result})
