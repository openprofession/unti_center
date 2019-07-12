import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

from center.dash_views import dictfetchall
from center.sql import users, auction, redcards, events


@cache_page(60)
def dash_auction_result(request, auction_id=12, date=(datetime.now() + timedelta(hours=3)).date()):
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


@cache_page(60)
def dash_auction_progress(request, date=(datetime.now())):
    auction_id = 14
    try:
        cursor = connections['dwh'].cursor()
        # cursor.execute(auction.auction_events_2)
        # df = pd.DataFrame(dictfetchall(cursor))
        # if not df.empty:
        #     df_info = pd.DataFrame()
        #     for event in df.event_uuid.unique():
        #         df_event = df[df["event_uuid"] == event]
        #         df_info = df_info.append(
        #             {'event_uuid': event, 'event_title': df_event.event_title.iloc[0],
        #             'sizeMax': df_event.sizeMax.iloc[0]},
        #                 ignore_index=True)
        #
        #     df_user_count = df.pivot_table(index=["event_uuid"], values="userID", columns="type",
        #                                        aggfunc=lambda x: len(x),
        #                                        fill_value=0, dropna=False)
        #     df_user_count.reset_index(inplace=True)
        #     result = df_user_count.set_index("event_uuid").join(df_info.set_index("event_uuid"))
        #     result["free_after_auction"] = result["sizeMax"] - result["auction_priority"]
        #     result["free_after_auction"][result["free_after_auction"] < 0] = 0
        #     result["free_now"] = result["sizeMax"] - result["auction_priority"] - result["manual"]
        #     result["free_now"][result["free_now"] < 0] = 0
        #     result = result[result["free_now"] > 0]
        #     result.sort_values("free_now", ascending=False, inplace=True)
        #     result_dict = result.to_dict('records')

        cursor.execute(auction.auction_one_by_id, [auction_id])
        df = pd.DataFrame(dictfetchall(cursor))
        if not df.empty:
            df["bet_count"] = 0
            data = {"auctions": []}
            df = df.groupby("event_uuid").count()
            df.reset_index(inplace=True)
            df_count = df[["event_uuid", "bet_count"]]
            df_count["interval"] = (round((df_count["bet_count"] - 5) / 10) + 1) * 10
            df_count["interval"] = df_count["interval"].astype(int)
            df_count["event_count"] = 0
            df_count = df_count.groupby("interval").count().reset_index()
            df_count = df_count[["interval", "event_count"]]
            data_to_graph_hist = df_count.values.tolist()

        cursor.execute(auction.auction_bets_by_id, [auction_id])
        df_auction = pd.DataFrame(dictfetchall(cursor))
        if not df.empty:
            df_event_count = df_auction.groupby("event_title").nunique()
            # считаем количество мероприятий, на которые сделали ставки <20% участников
            # event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            df_rating = df_event_count[["untiID"]].reset_index()
            df_rating.sort_values("untiID", ascending=False, inplace=True)
            # рейтинг в виде словаря
            event_rating = df_rating.to_dict('records')

            df_auction["bet_count"] = 0
            # считаем число участников, сделавших ставки
            user_count = df_auction["untiID"].nunique()

            # считаем число мероприятий, участвующих в аукционе. !!! Пока без мероприятий без ставок
            event_count = df_auction["event_uuid"].nunique()

            # дата окончания аукциона
            endDT = df_auction["endDT"].iloc[0]

            # считаем количество мероприятий, на которые сделали ставки <20% участников
            df_event_count = df_auction.groupby("event_uuid").nunique()
            event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            # разбиваем временную ось совершения ставок на интервалу по часу и считаем количество сделанных ставок,
            # в момент времени и накопительно
            df_auction.loc[1, 'bet_dt'] = df_auction['startDT'].iloc[0]
            df_auction.loc[-1, 'bet_dt'] = df_auction['endDT'].iloc[0]
            df_count = df_auction.groupby(pd.Grouper(key='bet_dt', freq='5Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["bet_dt"], 'count': df_count["bet_count"]}).set_index(
                "time").cumsum().reset_index()
            df_cumsum["N"] = df_cumsum.index
            df_cumsum["time"] = df_cumsum["time"].dt.hour + 3
            df_cumsum_series = df_cumsum[["N", "count"]]
            df_cumsum_ticks = df_cumsum[["N", "time"]].iloc[::12, :]

            # считаем общее количетсво ставок
            bet_count = df_cumsum_series["count"].iloc[-1]

            # готовим данные для построения графика в формате list of lists
            data_to_graph_dyn = df_cumsum_series.values.tolist()
            data_to_graph_ticks = df_cumsum_ticks.values.tolist()
            print(data_to_graph_ticks)
            df_top_bets = df_auction.sort_values(by='bet', ascending=False).head(10)

        cursor.execute(users.users_island_tag_count)
        all_user_count = 1541  # cursor.fetchone()[0]
    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/auction_2.html", {
        # 'event_rating': result_dict,
        'event_bet_hist_data': data_to_graph_hist,
        'event_list': event_rating, "title": df_auction['title'].iloc[0], "endDT": endDT, "user_count": user_count,
        "events_count": event_count, "bet_count": bet_count,
        "event_unpopular_count": event_unpopular_count, "event_bet_dyn_data": data_to_graph_dyn, "event_bet_dyn_ticks": data_to_graph_ticks,
        'all_user_count': all_user_count, 'top_bets': df_top_bets.to_dict('records')
    })
