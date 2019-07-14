from collections import namedtuple

import pandas as pd
from django.db import connections, OperationalError, ProgrammingError
from django.shortcuts import render

# PROD DATA
from django.utils.html import escape
from django.views.decorators.cache import cache_page

from center import settings
from center.sql import users, auction


@cache_page(settings.PAGE_CACHE_TIME)
def dash_all(request):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(users.users_island_tag_count)
        user_count = 1541  # cursor.fetchone()[0]
        cursor.execute(users.users_active_lk_today)
        users_active_lk_today = cursor.fetchone()[0]
        cursor.execute(users.users_active_lk_all)
        users_active_lk_all = cursor.fetchone()[0]
        cursor.execute(users.users_active_mob_today)
        users_active_mob_today = cursor.fetchone()[0]
        cursor.execute(users.users_active_mob_all)
        users_active_mob_all = cursor.fetchone()[0]
        cursor.execute(users.users_registered)

        df = pd.DataFrame(dictfetchall(cursor))
        data_to_graph = []
        if not df.empty:
            df["reg_count"] = 0
            df_count = df.groupby(pd.Grouper(key='regdt', freq='15Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["regdt"], 'count': df_count["reg_count"]}).set_index(
                "time").cumsum().reset_index()
            # df_cumsum = df_cumsum[df_cumsum["time"] >= "2019-07-09"]
            # если по оси x не time
            df_cumsum["time"] = df_cumsum["time"].dt.hour + 3
            df_cumsum["N"] = df_cumsum.index
            df2 = df_cumsum[["N", 'time']]
            df_cumsum = df_cumsum[["N", "count"]]

            register_count = df_cumsum["count"].iloc[-1]
            # в формате list of lists
            data_to_graph = df_cumsum.values.tolist()
            data_to_graph_series = df2.values.tolist()
            print(data_to_graph_series)

        cursor.execute(auction.auction_bets_1)
        df_auction = pd.DataFrame(dictfetchall(cursor))
        register_count = 0
        data_to_graph_series = []
        endDT = 0
        bet_count = 0
        data_to_graph_dyn = []
        auction_user_count = 0
        if not df.empty:
            df_event_count = df_auction.groupby("event_title").nunique()
            # считаем количество мероприятий, на которые сделали ставки <20% участников
            # event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            df_rating = df_event_count[["untiID"]].reset_index()
            df_rating.sort_values("untiID", ascending=False, inplace=True)
            df_rating = df_rating.head(5)
            # рейтинг в виде словаря
            event_rating = df_rating.to_dict('records')

            df_auction["bet_count"] = 0
            # считаем число участников, сделавших ставки
            auction_user_count = df_auction["untiID"].nunique()

            # считаем число мероприятий, участвующих в аукционе. !!! Пока без мероприятий без ставок
            event_count = df_auction["event_uuid"].nunique()

            # дата окончания аукциона
            endDT = df_auction["endDT"].iloc[0]

            # считаем количество мероприятий, на которые сделали ставки <20% участников
            df_event_count = df_auction.groupby("event_uuid").nunique()
            event_unpopular_count = len(df_event_count[df_event_count["untiID"] / auction_user_count < 0.2])

            # разбиваем временную ось совершения ставок на интервалу по часу и считаем количество сделанных ставок,
            # в момент времени и накопительно
            df_count = df_auction.groupby(pd.Grouper(key='bet_dt', freq='60Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["bet_dt"], 'count': df_count["bet_count"]}).set_index(
                "time").cumsum().reset_index()
            df_cumsum["N"] = df_cumsum.index
            df_cumsum = df_cumsum[["N", "count"]]

            # считаем общее количетсво ставок
            bet_count = df_cumsum["count"].iloc[-1]

            # готовим данные для построения графика в формате list of lists
            data_to_graph_dyn = df_cumsum.values.tolist()
    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")
    except ProgrammingError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/all.html", {
        'user_count': user_count,
        'users_active_lk_today': users_active_lk_today,
        'users_active_lk_all': users_active_lk_all,
        'users_active_mob_today': users_active_mob_today,
        'users_active_mob_all': users_active_mob_all,
        'users_registered_count': register_count,
        'users_registered_data': data_to_graph,
        'users_registered_data_series': data_to_graph_series,
        "title": df_auction['title'].iloc[0], "endDT": endDT,
        "bet_count": bet_count, "event_bet_dyn_data": data_to_graph_dyn,
        'auction_user_count': auction_user_count
    })


def dash_auctions(request):
    return render(request, "dashboards/prod/auctions.html", {
    })


@cache_page(settings.PAGE_CACHE_TIME)
def dash_auction_one(request):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(auction.auction_events_1)
        df = pd.DataFrame(dictfetchall(cursor))
        if not df.empty:
            df_info = pd.DataFrame()
            for event in df.event_uuid.unique():
                df_event = df[df["event_uuid"] == event]
                df_info = df_info.append(
                    {'event_uuid': event, 'event_title': df_event.event_title.iloc[0],
                     'sizeMax': df_event.sizeMax.iloc[0]},
                    ignore_index=True)

            df_user_count = df.pivot_table(index=["event_uuid"], values="userID", columns="type",
                                           aggfunc=lambda x: len(x),
                                           fill_value=0, dropna=False)
            df_user_count.reset_index(inplace=True)
            result = df_user_count.set_index("event_uuid").join(df_info.set_index("event_uuid"))
            result["free_after_auction"] = result["sizeMax"] - result["auction_priority"]
            result["free_after_auction"][result["free_after_auction"] < 0] = 0
            result["free_now"] = result["sizeMax"] - result["auction_priority"] - result["manual"]
            result["free_now"][result["free_now"] < 0] = 0
            result = result[result["free_now"] > 0]
            result.sort_values("free_now", ascending=False, inplace=True)
            result_dict = result.to_dict('records')

        cursor.execute(auction.auction_one_1)
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

        cursor.execute(auction.auction_bets_1)
        df_auction = pd.DataFrame(dictfetchall(cursor))
        if not df.empty:
            df_event_count = df_auction.groupby("event_title").nunique()
            # считаем количество мероприятий, на которые сделали ставки <20% участников
            # event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            df_rating = df_event_count[["untiID"]].reset_index()
            df_rating.sort_values("untiID", ascending=False, inplace=True)
            df_rating = df_rating.head(5)
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
            df_count = df_auction.groupby(pd.Grouper(key='bet_dt', freq='60Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["bet_dt"], 'count': df_count["bet_count"]}).set_index(
                "time").cumsum().reset_index()
            df_cumsum["N"] = df_cumsum.index
            df_cumsum = df_cumsum[["N", "count"]]

            # считаем общее количетсво ставок
            bet_count = df_cumsum["count"].iloc[-1]

            # готовим данные для построения графика в формате list of lists
            data_to_graph_dyn = df_cumsum.values.tolist()

        cursor.execute(users.users_island_tag_count)
        all_user_count = 1541  # cursor.fetchone()[0]
    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/auction_one.html", {
        'event_rating': result_dict,
        'event_bet_hist_data': data_to_graph_hist,
        'event_list': event_rating, "title": df_auction['title'].iloc[0], "endDT": endDT, "user_count": user_count,
        "events_count": event_count, "bet_count": bet_count,
        "event_unpopular_count": event_unpopular_count, "event_bet_dyn_data": data_to_graph_dyn,
        'all_user_count': all_user_count
    })

    # UTILS


@cache_page(settings.PAGE_CACHE_TIME)
def dash_auction_labs_1(request):
    try:
        cursor = connections['dwh'].cursor()
        cursor.execute(auction.auction_events_1)
        df = pd.DataFrame(dictfetchall(cursor))
        if not df.empty:
            df_info = pd.DataFrame()
            for event in df.event_uuid.unique():
                df_event = df[df["event_uuid"] == event]
                df_info = df_info.append(
                    {'event_uuid': event, 'event_title': df_event.event_title.iloc[0],
                     'sizeMax': df_event.sizeMax.iloc[0]},
                    ignore_index=True)

            df_user_count = df.pivot_table(index=["event_uuid"], values="userID", columns="type",
                                           aggfunc=lambda x: len(x),
                                           fill_value=0, dropna=False)
            df_user_count.reset_index(inplace=True)
            result = df_user_count.set_index("event_uuid").join(df_info.set_index("event_uuid"))
            result["free_after_auction"] = result["sizeMax"] - result["auction_priority"]
            result["free_after_auction"][result["free_after_auction"] < 0] = 0
            result["free_now"] = result["sizeMax"] - result["auction_priority"] - result["manual"]
            result["free_now"][result["free_now"] < 0] = 0

            result_sum = result.agg(['sum'])
            result_sum_dict = result_sum.to_dict('records')
            result = result[result["free_now"] > 0]
            result.sort_values("free_now", ascending=False, inplace=True)
            result_dict = result.to_dict('records')

        cursor.execute(auction.auction_one_1)
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

        cursor.execute(auction.auction_bets_1)
        df_auction = pd.DataFrame(dictfetchall(cursor))
        if not df.empty:
            df_event_count = df_auction.groupby("event_title").nunique()
            # считаем количество мероприятий, на которые сделали ставки <20% участников
            # event_unpopular_count = len(df_event_count[df_event_count["untiID"] / user_count < 0.2])

            df_rating = df_event_count[["untiID"]].reset_index()
            df_rating.sort_values("untiID", ascending=False, inplace=True)

            df_rating = df_rating.head(15)
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
            df_count = df_auction.groupby(pd.Grouper(key='bet_dt', freq='60Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["bet_dt"], 'count': df_count["bet_count"]}).set_index(
                "time").cumsum().reset_index()
            df_cumsum["N"] = df_cumsum.index
            df_cumsum = df_cumsum[["N", "count"]]

            # считаем общее количетсво ставок
            bet_count = df_cumsum["count"].iloc[-1]

            # готовим данные для построения графика в формате list of lists
            data_to_graph_dyn = df_cumsum.values.tolist()

        cursor.execute(users.users_island_tag_count)
        all_user_count = 1541  # cursor.fetchone()[0]
    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")

    return render(request, "dashboards/prod/auction_labs_1.html", {
        'event_rating': result_dict,
        'event_bet_hist_data': data_to_graph_hist,
        'event_list': event_rating, "title": df_auction['title'].iloc[0], "endDT": endDT, "user_count": user_count,
        "events_count": event_count, "bet_count": bet_count,
        "event_unpopular_count": event_unpopular_count, "event_bet_dyn_data": data_to_graph_dyn,
        'all_user_count': all_user_count, "rating_sum": result_sum_dict
    })


@cache_page(settings.PAGE_CACHE_TIME)
def dash_auction_2(request):
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

        cursor.execute(auction.auction_one_2)
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

        cursor.execute(auction.auction_bets_2)
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
            df_count = df_auction.groupby(pd.Grouper(key='bet_dt', freq='5Min')).count().reset_index()
            df_cumsum = pd.DataFrame({'time': df_count["bet_dt"], 'count': df_count["bet_count"]}).set_index(
                "time").cumsum().reset_index()
            df_cumsum["N"] = df_cumsum.index
            df_cumsum = df_cumsum[["N", "count"]]

            # считаем общее количетсво ставок
            bet_count = df_cumsum["count"].iloc[-1]

            # готовим данные для построения графика в формате list of lists
            data_to_graph_dyn = df_cumsum.values.tolist()
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
        "event_unpopular_count": event_unpopular_count, "event_bet_dyn_data": data_to_graph_dyn,
        'all_user_count': all_user_count, 'top_bets': df_top_bets.to_dict('records')
    })
    # UTILS


@cache_page(settings.PAGE_CACHE_TIME)
def dash_auction_3(request):
    auction_id = 12
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

@cache_page(settings.PAGE_CACHE_TIME)
def dash_auction_4(request):
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

def event_feedback(request):
    return render(request, "dashboards/prod/feedback_i.html")

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
