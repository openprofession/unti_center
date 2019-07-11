import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events


@cache_page(60)
def dash_auction_result(request, date='2019-07-11'):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(events.enrolls_auction_2)
        enrolls_df = pd.DataFrame(dictfetchall(cursor))
        result = {}
        if not enrolls_df.empty:
            # result['enrolls'] = enrolls_df.to_dict('records')
            enrolls_df['manual'] = pd.np.where(enrolls_df['type'] == 'manual', 1, 0)
            enrolls_df['auction_bet'] = pd.np.where(enrolls_df['type'] == 'auction_bet', 1, 0)
            enrolls_df['auction_priority'] = pd.np.where(enrolls_df['type'] == 'auction_priority', 1, 0)
            enrolls_event_df = enrolls_df.groupby('event_id').agg(
                {'userID': 'count', 'sizeMin': 'first', 'sizeMax': 'first', 'event_id': 'first', 'title': 'first',
                 'auction_bet': 'sum', 'manual': 'sum', 'place_title': 'first'})
            enrolls_event_df['free'] = enrolls_event_df.eval('sizeMax-userID')
            enrolls_event_df = enrolls_event_df.sort_values(by='free', ascending=False)

            result['enrolls_by_event'] = enrolls_event_df.to_dict('records')
            enrolls_event_top_df = enrolls_event_df.sort_values(by='userID', ascending=False)
            result['enrolls_by_event_top'] = enrolls_event_top_df.to_dict('records')
            result['user_count'] = enrolls_df['userID'].nunique()

    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/auction_sm.html", {'result': result, 'date': date})
