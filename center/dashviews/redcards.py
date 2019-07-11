import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, teams


@cache_page(settings.PAGE_CACHE_TIME)
def dash_redcards(request):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(redcards.all_public_cards)
        cards_df = pd.DataFrame(dictfetchall(cursor))
        cursor.execute(teams.user_teams)
        teams_df = pd.DataFrame(dictfetchall(cursor))
        cards_df = cards_df.join(teams_df, lsuffix='leader_id', rsuffix='leaderID')
        result = {}
        if not cards_df.empty:
            result['count_red_issued'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'issued')]['uuid'].nunique()
            result['count_red_published'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'published')]['uuid'].nunique()
            result['count_red_consideration'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'consideration')]['uuid'].nunique()
            result['count_red_public'] = \
                cards_df[(cards_df.type == 'red') & ((cards_df.status == 'issued') | (cards_df.status == 'published') | (cards_df.status == 'consideration'))]['uuid'].nunique()
            result['count_red_initiated'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'initiated')]['uuid'].nunique()
            result['count_yellow'] = cards_df[(cards_df.type == 'yellow')]['uuid'].nunique()
            result['count_green'] = cards_df[(cards_df.type == 'green')]['uuid'].nunique()
            result['cards'] = cards_df.to_dict('record')
            cards_df['red'] = pd.np.where(cards_df['type'] == 'red', 1, 0)
            cards_df['yellow'] = pd.np.where(cards_df['type'] == 'yellow', 1, 0)
            cards_df['green'] = pd.np.where(cards_df['type'] == 'green', 1, 0)
            result['rating'] = cards_df.groupby('team_title').agg({'red': 'sum', 'yellow': 'sum', 'green': 'sum', 'team_title': 'first'}). \
                sort_values(by='red', ascending=False).to_dict('record')
            cards_data_df = cards_df
            cards_data_df.loc[-1, 'change_dt'] = pd.Timestamp('2019-07-10 00:00')
            cards_data_df = cards_data_df.groupby(pd.Grouper(key='change_dt', freq='H')).agg({'red': 'sum', 'yellow': 'sum', 'green': 'sum'}).cumsum().reset_index()
            cards_data_df["N"] = cards_data_df.index
            result['red_cards_data'] = cards_data_df[["N", "red"]].values.tolist()
            result['yellow_cards_data'] = cards_data_df[["N", "yellow"]].values.tolist()
            result['green_cards_data'] = cards_data_df[["N", "green"]].values.tolist()

    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/redcards.html", {'result': result})
