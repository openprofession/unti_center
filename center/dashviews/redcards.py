import pandas as pd
from django.db import connections, OperationalError
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from center import settings
from center.dash_views import dictfetchall
from center.sql import users, auction, redcards


@cache_page(settings.PAGE_CACHE_TIME)
def dash_redcards(request):
    try:
        cursor = connections['dwh-test'].cursor()
        cursor.execute(redcards.all_public_cards)
        cards_df = pd.DataFrame(dictfetchall(cursor))
        result = []
        if not cards_df.empty:
            print(cards_df)

    except OperationalError:
        print('Operational fail')
        return render(request, "fail.html")
