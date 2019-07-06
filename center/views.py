from collections import namedtuple
from datetime import date

from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render

from center.models import Dashboard, Report
from center.utils import daterange


def dashboards(request):
    dashboard_list = Dashboard.objects.filter(active=True, public=True)
    return render(request, 'dashboard_list.html', {'dashboards': dashboard_list})


def reports(request):
    report_list = Report.objects.filter(active=True, public=True)
    return render(request, 'report_list.html', {'reports': report_list})


def main(request):
    cursor = connections['dwh-test'].cursor()
    cursor.execute(
        "SELECT group_concat(tag.title) AS tag_titles, CASE WHEN  group_concat(tag.title) LIKE '%testregister%' THEN True ELSE False END AS registered, user_info.* FROM unti_ple.user_tag INNER JOIN unti_ple.tag ON unti_ple.user_tag.tagID = tag.id INNER JOIN unti_ple.user_info ON user_info.userID = user_tag.userID WHERE tag.title LIKE 'island1022-yes-test%'  GROUP BY  user_info.id")
    users_island = dictfetchall(cursor)
    cursor.execute(
        "SELECT  auction.*,  COUNT(user_auction.id) AS activities,  SUM(user_auction.bet) AS bets FROM xle_dev.user_auction  INNER JOIN xle_dev.auction    ON user_auction.auctionID = auction.id WHERE auction.status = 'opened' AND auction.active = 1 AND auction.contextID = 13 ")
    open_auctions = dictfetchall(cursor)
    cursor.execute(
        "SELECT count(user_auction.priority) as priorities, sum(user_auction.bet) as bets, COUNT(user_auction.id) AS activities , event.title AS event_title FROM xle_dev.user_auction  INNER JOIN xle_dev.auction ON user_auction.auctionID = auction.id  INNER JOIN xle_dev.event    ON user_auction.eventID = event.id WHERE auction.status = 'opened' AND auction.active = 1 AND auction.contextID=13 GROUP BY event.title ORDER BY bets DESC, event_title")
    open_auction_bets = dictfetchall(cursor)
    cursor.execute(
        "SELECT event.*, COUNT(checkin.id)/2 AS checkins, GROUP_CONCAT(tag.title) AS tag_titles, GROUP_CONCAT(checkin.userID) AS users FROM xle_dev.event INNER JOIN xle_dev.context_run ON event.runID = context_run.runID INNER JOIN xle_dev.checkin   ON checkin.eventID = event.id  LEFT OUTER JOIN xle_dev.user_tag ON checkin.userID = user_tag.userID  INNER JOIN xle_dev.tag    ON user_tag.tagID = tag.id WHERE context_run.contextID = 13 AND tag.title LIKE '%testgroup%' GROUP BY event.uuid ORDER BY checkins desc ")
    chekins = dictfetchall(cursor)
    return render(request, "dashboards/main.html",
                  {"open_auctions": open_auctions, "open_auction_bets": open_auction_bets,
                   "users_island": users_island, "checkins": chekins})


def attendance_dtrace(request):
    filter_date = daterange(date(2019, 7, 10), date(2019, 7, 22))
    filter_event_type = [{'title': 'Мастер класс'}, {'title': 'Лекции'}, {'title': 'Спорт'}]
    filter_faculty = [{'title': 'Мастер класс'}, {'title': 'Лекции'}, {'title': 'Спорт'}]
    filter_team = [{'title': 'Команда 1'}, {'title': 'Команда 2'}, {'title': 'Команда 3'}]

    return render(request, "dashboards/attendance_dtrace.html", {
        'filter_date': filter_date,
        'filter_event_type': filter_event_type,
        'filter_faculty': filter_faculty,
        'filter_team': filter_team,
    })


def run_report(request):
    report = Report.objects.first()
    cursor = connections[report.source_db].cursor()
    cursor.execute(report.sql)
    result = dictfetchall(cursor)
    return HttpResponse(result)


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
