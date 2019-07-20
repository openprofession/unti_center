import json

import pandas as pd
import requests
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events, sport, teams, edumap


# @cache_page(120 or settings.PAGE_CACHE_TIME)
def dash_edumap_rating(request):
    result = {}
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(edumap.edumap_agr_likes)
        agr_likes_df = pd.DataFrame(dictfetchall(cursor))

        print(agr_likes_df.shape)
        print(agr_likes_df.columns)

        result['agr_rating'] = ""

    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/edumap.html", {'result': result})
