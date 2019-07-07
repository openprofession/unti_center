from collections import namedtuple
from datetime import date

from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.views import logout_then_login as base_logout
from center.models import Dashboard, Report
from center.utils import daterange


def logout(request):
    return base_logout(request, login_url="/")


def dashboards(request):
    dashboard_list = Dashboard.objects.filter(active=True, public=True)
    return render(request, 'public/dashboard_list.html', {'dashboards': dashboard_list})


def reports(request):
    report_list = Report.objects.filter(active=True, public=True)
    return render(request, 'public/report_list.html', {'reports': report_list})


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


def demo(request):
    cursor = connections['dwh-test'].cursor()
    cursor.execute(
        """SELECT
  `xle_dev`.`auction`.`uuid` AS `uuid`,
  `xle_dev`.`auction`.`title` AS `title`,
  `xle_dev`.`auction`.`type` AS `type`,
  `xle_dev`.`auction`.`status` AS `status`,
  `xle_dev`.`auction`.`startDT` AS `startDT`,
  `xle_dev`.`auction`.`endDT` AS `endDT`,
  `xle_dev`.`auction`.`active` AS `active`,
  SUM(`xle_dev`.`user_auction`.`bet`) AS `bets_sum`,
  count(`xle_dev`.`user_auction`.`bet`) AS `bets_count`,
  count(DISTINCT(`xle_dev`.`user_info`.`untiID`)) AS `user_count`
FROM ((`xle_dev`.`auction`
  LEFT JOIN `xle_dev`.`user_auction`
    ON (`xle_dev`.`user_auction`.`auctionID` = `xle_dev`.`auction`.`id`))
  LEFT JOIN `xle_dev`.`user_info`
    ON (`xle_dev`.`user_auction`.`userID` = `xle_dev`.`user_info`.`userID`))
WHERE `xle_dev`.`auction`.`contextID` = 23""")
    auction_total = dictfetchall(cursor)

    cursor.execute("""SELECT
  auction.uuid AS uuid,
  auction.title AS title,
  auction.type AS type,
  auction.status AS status,
  auction.startDT AS startDT,
  auction.endDT AS endDT,
  auction.active AS active,
  SUM(user_auction.bet) AS bets_sum,
  COUNT(user_auction.bet) AS bets_count,
  event.title AS event_title
FROM xle_dev.auction
  LEFT OUTER JOIN xle_dev.user_auction
    ON user_auction.auctionID = auction.id
  LEFT OUTER JOIN xle_dev.user_info
    ON user_auction.userID = user_info.userID
  LEFT OUTER JOIN xle_dev.event
    ON user_auction.eventID = event.id
WHERE auction.contextID = 23
GROUP BY user_auction.eventID
  ORDER BY bets_sum DESC""")
    auction_events = dictfetchall(cursor)
    return render(request, "dashboards/demo.html", {'auction_total': auction_total, 'auction_events': auction_events})


def demo_timetable(request):
    cursor = connections['dwh-test'].cursor()
    cursor.execute("""SELECT
  Count(user_info.untiID) AS users,
  user_info.leaderID,
  user_info.firstname,
  user_info.lastname,
  user_info.middlename,
  activity.title
FROM  xle_dev.timetable
  LEFT OUTER JOIN xle_dev.run
    ON timetable.runID = run.id
  LEFT OUTER JOIN  xle_dev.context_run
    ON timetable.runID = context_run.runID
  LEFT OUTER JOIN  xle_dev.user_info
    ON timetable.userID = user_info.userID
  LEFT OUTER JOIN  xle_dev.activity
    ON run.activityID = activity.id
WHERE context_run.contextID = 23
  GROUP BY activity.id
ORDER BY USERS desc""")
    event_enrolls = dictfetchall(cursor)
    cursor.execute("""SELECT
      Count(activity.title) AS events,
      user_info.leaderID,
      user_info.firstname,
      user_info.lastname,
      user_info.middlename
    FROM xle_dev.timetable
      LEFT OUTER JOIN xle_dev.run
        ON timetable.runID = run.id
      LEFT OUTER JOIN xle_dev.context_run
        ON timetable.runID = context_run.runID
      LEFT OUTER JOIN xle_dev.user_info
        ON timetable.userID = user_info.userID
      LEFT OUTER JOIN xle_dev.activity
        ON run.activityID = activity.id
    WHERE context_run.contextID = 23
      GROUP BY user_info.untiID
    ORDER BY events desc""")
    user_enrolls = dictfetchall(cursor)
    return render(request, "dashboards/demo_timetable.html",
                  {'event_enrolls': event_enrolls, 'user_enrolls': user_enrolls})


def demo_feedback(request):
    cursor = connections['dwh-test'].cursor()
    cursor.execute("""SELECT
  user_feedback_answer.userID AS userID,
  user_feedback_answer.eventID AS eventID,
  AVG(user_feedback_answer.value) AS value_avg,
  MIN(user_feedback_answer.value) AS value_min,
  COUNT(user_feedback_answer.value) AS value_count,
  user_feedback_answer.createDT AS createDT,
  feedback_question.title AS title,
  feedback_question.type AS type,
  event.title AS event_title
FROM xle_dev.user_feedback_answer
  LEFT OUTER JOIN xle_dev.feedback_question
    ON user_feedback_answer.feedbackQuestionID = feedback_question.id
  LEFT OUTER JOIN xle_dev.event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN xle_dev.run
    ON event.runID = run.id
  LEFT OUTER JOIN xle_dev.context_run
    ON run.id = context_run.runID
WHERE xle_dev.feedback_question.type = 'rating'
     AND context_run.contextID = 23
GROUP BY event_title""")
    event_feedback_score = dictfetchall(cursor)
    return render(request, "dashboards/demo_feedback.html",
                  {'event_feedback': event_feedback_score})


def demo_test(request):
    return render(request, "dashboards/demo_test.html")


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
