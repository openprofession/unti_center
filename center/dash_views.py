from collections import namedtuple

import pandas as pd
from django.db import connections
from django.shortcuts import render

# PROD DATA
from django.utils.html import escape

from center.sql import users


def dash_all(request):
    cursor = connections['dwh'].cursor()
    cursor.execute(users.users_island_tag_count)
    user_count = cursor.fetchone()[0]
    cursor.execute(users.users_active_lk_today)
    users_active_lk_today = cursor.fetchone()[0]
    cursor.execute(users.users_active_lk_all)
    users_active_lk_all = cursor.fetchone()[0]
    cursor.execute(users.users_active_mob_today)
    users_active_mob_today = cursor.fetchone()[0]
    cursor.execute(users.users_active_mob_all)
    users_active_mob_all = cursor.fetchone()[0]
    cursor.execute(users.users_registered)
    # registr = cursor.fetchall()
    df = pd.DataFrame(dictfetchall(cursor))
    data_to_graph = []
    if not df.empty:
        df["reg_count"] = 0
        df_count = df.groupby(pd.Grouper(key='regdt', freq='15Min')).count().reset_index()
        df_cumsum = pd.DataFrame({'time': df_count["regdt"], 'count': df_count["reg_count"]}).set_index(
            "time").cumsum().reset_index()
        #df_cumsum = df_cumsum[df_cumsum["time"] >= "2019-07-09"]
        # если по оси x не time
        df_cumsum["time"] = df_cumsum["time"].dt.hour+3
        df_cumsum["N"] = df_cumsum.index
        df2 = df_cumsum[["N", 'time']]
        df_cumsum = df_cumsum[["N", "count"]]

        register_count = df_cumsum["count"].iloc[-1]
        # в формате list of lists
        data_to_graph = df_cumsum.values.tolist()
        data_to_graph_series = df2.values.tolist()
        print(data_to_graph_series)

    return render(request, "dashboards/prod/all.html", {
        'user_count': user_count,
        'users_active_lk_today': users_active_lk_today,
        'users_active_lk_all': users_active_lk_all,
        'users_active_mob_today': users_active_mob_today,
        'users_active_mob_all': users_active_mob_all,
        'users_registered_count': register_count,
        'users_registered_data': data_to_graph,
        'users_registered_data_series': data_to_graph_series,
    })


def dash_auction(request):
    return render(request, "dashboards/prod/auction.html", {
    })


def dash_add_enroll(request):
    return render(request, "dashboards/prod/auction.html", {
    })


# UTILS
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
