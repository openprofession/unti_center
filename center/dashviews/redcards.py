import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, teams


#@cache_page(settings.PAGE_CACHE_TIME)
def dash_redcards(request):
    # return render(request, "fail.html")

    cursor = connections['dwh'].cursor()
    cursor.execute(redcards.all_public_cards)
    cards_load_df = pd.DataFrame(dictfetchall(cursor))
    print(cards_load_df.shape)
    cursor.execute(users.users_island_tag)
    user_df = pd.DataFrame(dictfetchall(cursor))
    cursor.execute(teams.user_teams)
    teams_load_df = pd.DataFrame(dictfetchall(cursor))
    teams_df = user_df.merge(teams_load_df, on='leaderID', how='left')
    print(teams_df.shape)
    cards_df = cards_load_df.merge(teams_df, on='leaderID', how='outer')
    print(cards_df.shape)

    result = {}
    if not cards_df.empty:
        result['count_red_issued'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'issued')]['uuid'].nunique()
        result['count_red_published'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'published')]['uuid'].nunique()
        result['count_red_consideration'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'consideration')]['uuid'].nunique()
        result['count_red_eliminated'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'eliminated')]['uuid'].nunique()

        result['count_red_public'] = \
            cards_df[(cards_df.type == 'red') & ((cards_df.status == 'issued') | (cards_df.status == 'published') | (cards_df.status == 'consideration'))]['uuid'].nunique()
        result['count_red_initiated'] = cards_df[(cards_df.type == 'red') & (cards_df.status == 'initiated')]['uuid'].nunique()
        result['count_yellow'] = cards_df[(cards_df.type == 'yellow')]['uuid'].nunique()
        result['count_green'] = cards_df[(cards_df.type == 'green')]['uuid'].nunique()
        result['cards'] = cards_df.to_dict('record')
        cards_df['red'] = pd.np.where((cards_df['type'] == 'red') & (cards_df['status'] != 'eliminated'), 1, 0)
        cards_df['yellow'] = pd.np.where(cards_df['type'] == 'yellow', 1, 0)
        cards_df['green'] = pd.np.where(cards_df['type'] == 'green', 1, 0)
        personal_rating_df = cards_df.groupby('leaderID').agg(
            {'red': 'sum', 'yellow': 'sum', 'green': 'sum', 'team_title': 'first', 'firstname': 'first', 'lastname': 'first'})
        personal_rating_df['score'] = personal_rating_df['green'] - personal_rating_df['red']
        personal_rating_df = personal_rating_df.replace('-', None)
        # personal_rating_df['team'] = pd.np.where(personal_rating_df['team_title'] == 'None', '-', personal_rating_df['team_title'])
        personal_rating_df = personal_rating_df.sort_values(by='score', ascending=False).reset_index().sort_values(by='score', ascending=True)
        personal_rating_df["N"] = personal_rating_df.index + 1

        result['personal_rating'] = personal_rating_df.to_dict('record')
        team_rating_df = cards_df.groupby('team_title').agg({'red': 'sum', 'yellow': 'sum', 'green': 'sum', 'team_title': 'first', 'leaderID': 'nunique'})
        team_rating_df['score'] = team_rating_df['green'] - team_rating_df['red']
        team_rating_df = team_rating_df.sort_values(by='score', ascending=False).set_index("team_title").reset_index()
        team_rating_df["N"] = team_rating_df.index + 1
        result['rating'] = team_rating_df.sort_values(by='N', ascending=True).to_dict('record')
        cards_data_df = cards_df
        cards_data_df.loc[-1, 'change_dt'] = pd.Timestamp('2019-07-10 00:00')
        cards_data_df = cards_data_df.groupby(pd.Grouper(key='change_dt', freq='H')).agg({'red': 'sum', 'yellow': 'sum', 'green': 'sum'}).cumsum().reset_index()
        cards_data_df["N"] = cards_data_df.index
        result['red_cards_data'] = cards_data_df[["N", "red"]].values.tolist()
        result['yellow_cards_data'] = cards_data_df[["N", "yellow"]].values.tolist()
        result['green_cards_data'] = cards_data_df[["N", "green"]].values.tolist()

    return render(request, "dashboards/prod/redcards.html", {'result': result})
