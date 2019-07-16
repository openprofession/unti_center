import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events


@cache_page(60)
def dash_auction_result(request, auction_id=None, date=(datetime.now() + timedelta(hours=3)).date()):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(events.enrolls_auction_2, [date])
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
            result['user_count_bet'] = enrolls_df['auction_bet'].sum()
            result['user_count_manual'] = enrolls_df['manual'].sum()

    except OperationalError as e:
        print(e)
        return render(request, "fail.html")

    return render(request, "dashboards/prod/auction_sm.html", {'result': result, 'date': date})


# @cache_page(60)
def dash_auction_progress(request, date=None, auction_id=None):
    result = {}
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(auction.auction_latest_id)

        if date:
            cursor.execute(auction.auction_bets_by_id, [id])
        else:
            if not auction_id:
                cursor.execute(auction.auction_latest_id)
                auction_id = cursor.fetchone()[0]
                cursor.execute(auction.auction_bets_by_id, [auction_id])
            cursor.execute(auction.auction_bets_by_id, [auction_id])
        df = pd.DataFrame(dictfetchall(cursor))
        print(auction_id)
        if not df.empty:
            df["bet_count"] = 0
            df = df.groupby("event_uuid").count()
            df.reset_index(inplace=True)
            df_count = df[["event_uuid", "bet_count"]]
            df_count["interval"] = (round((df_count["bet_count"] - 5) / 10) + 1) * 10
            df_count["interval"] = df_count["interval"].astype(int)
            df_count["event_count"] = 0
            df_count = df_count.groupby("interval").count().reset_index()
            df_count = df_count[["interval", "event_count"]]
            result['event_bet_hist_data'] = df_count.values.tolist()
        if date:
            cursor.execute(auction.auction_bets_by_date, [date])
        else:
            cursor.execute(auction.auction_bets_by_id, [auction_id])
        df_auction = pd.DataFrame(dictfetchall(cursor))
        if not df_auction.empty:
            result['top_bets'] = df_auction.sort_values(by='bet', ascending=False).head(20).to_dict('records')
            df_event_count = df_auction.groupby("event_title").nunique()
            # считаем количество мероприятий, на которые сделали ставки <20% участников
            # event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            df_rating = df_event_count[["untiID"]].reset_index()
            df_rating.sort_values("untiID", ascending=False, inplace=True)
            # рейтинг в виде словаря
            result['event_list'] = df_rating.to_dict('records')
            result['title'] = df_auction['title'].iloc[0]
            df_auction["bet_count"] = 0
            # считаем число участников, сделавших ставки
            result['user_count'] = df_auction["untiID"].nunique()

            # считаем число мероприятий, участвующих в аукционе. !!! Пока без мероприятий без ставок
            # event_count = df_auction["event_uuid"].nunique()

            # дата окончания аукциона
            result['endDT'] = df_auction["endDT"].iloc[0]

            # считаем количество мероприятий, на которые сделали ставки <20% участников
            result['event_count'] = df_auction.groupby("event_uuid").nunique()
            # event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            # разбиваем временную ось совершения ставок на интервалу по часу и считаем количество сделанных ставок,
            # в момент времени и накопительно
            df_auction.loc[1, 'bet_dt'] = df_auction['startDT'].iloc[0]
            # df_auction.loc[-1, 'bet_dt'] = df_auction['endDT'].iloc[0]
            df_count = df_auction.groupby(pd.Grouper(key='bet_dt', freq='5Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["bet_dt"], 'count': df_count["bet_count"]}).set_index("time").cumsum().reset_index()
            df_cumsum["N"] = df_cumsum.index
            df_cumsum["time1"] = df_cumsum["time"].dt.hour + 3
            df_cumsum_series = df_cumsum[["N", "count"]]
            df_cumsum_ticks = df_cumsum[["N", "time1"]].iloc[::12, :]

            # считаем общее количетсво ставок
            result['bet_count'] = df_cumsum_series["count"].iloc[-1]

            # готовим данные для построения графика в формате list of lists
            result['event_bet_dyn_data'] = df_cumsum_series.values.tolist()
            result['event_bet_dyn_ticks'] = df_cumsum_ticks.values.tolist()

        cursor.execute(users.users_island_tag_count)
        result['all_user_count'] = 1541  # cursor.fetchone()[0]

    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/auction.html", {'result': result})
