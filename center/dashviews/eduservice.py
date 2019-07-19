import json

import pandas as pd
import requests
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events, sport, teams


@cache_page(settings.PAGE_CACHE_TIME)
def dash_eduservice_rating(request):
    result = {}
    try:
        r = requests.post("https://eduservices.2035.university/rest/v2/oauth/token?grant_type=password&username=restapiuser&password=rV3EDzt3qptt",
                          headers={"content-type": "application/x-www-form-urlencoded",
                                   "Authorization": "Basic ZnE0aXk0cG1mcnA2c20xbTl6d3I6eHBwYXQ2MmZtczhqdGV1eHNleXZtZ3pveXQ4aG40bTk4aWFyem43aQ=="})

        data = json.loads(r.content.decode())

        token = data['access_token']

        r = requests.get("https://eduservices.2035.university/rest/v2/queries/srvcat_AgreementConfirm/agreementConfirmByDate?startDate=2019-07-01&endDate=2019-07-30",
                         headers={"Authorization": "Bearer {}".format(token)})

        agr_df = pd.read_json(r.content)
        print(agr_df.shape)
        print(agr_df.columns)
        # for agreement_data in payload:
        #    print('x')
    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/eduservice.html", {'result': result})
