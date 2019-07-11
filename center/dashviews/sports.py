import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events


# @cache_page(settings.PAGE_CACHE_TIME)
def dash_sports(request, date=(datetime.now() + timedelta(days=1)).date()):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(events.events_enroll_by_date_type, [192, date])
        enrolls_df = pd.DataFrame(dictfetchall(cursor))
        result = {}
        if not enrolls_df.empty:
            # result['enrolls'] = enrolls_df.to_dict('records')
            enrolls_event_df = enrolls_df.groupby('event_id').agg(
                {'userID': 'count', 'sizeMin': 'first', 'sizeMax': 'first', 'event_id': 'first', 'title': 'first'})
            enrolls_event_df['free'] = enrolls_event_df.eval('sizeMax-userID')
            enrolls_event_df = enrolls_event_df.sort_values(by='free', ascending=False)

            result['enrolls_by_event'] = enrolls_event_df.to_dict('records')
            enrolls_event_top_df = enrolls_event_df.sort_values(by='userID', ascending=False)
            result['enrolls_by_event_top'] = enrolls_event_top_df.to_dict('records')
            result['user_count'] = enrolls_df['userID'].nunique()

    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/sports.html", {'result': result, 'date': date})
