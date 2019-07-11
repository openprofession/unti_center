import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, teams, feedback


@cache_page(settings.PAGE_CACHE_TIME)
def dash_aim(request):
    # try:
    cursor = connections['dwh'].cursor()
    cursor.execute(feedback.aim_all)
    aims_df = pd.DataFrame(dictfetchall(cursor))
    cursor.execute(teams.user_teams)
    teams_df = pd.DataFrame(dictfetchall(cursor))
    aims_df = aims_df.join(teams_df, lsuffix='leaderID', rsuffix='leaderID')
    result = {}
    if not aims_df.empty:
        print(aims_df)

    # except OperationalError:
    #    print('Operational fail')
    #    return render(request, "fail.html")


    return render(request, "dashboards/prod/aims.html", {'result': result})
