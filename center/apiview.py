from django.db import connections


def teams(request):
    cursor = connections['dwh'].cursor()
    cursor.execute("select * from xle.activity")


def auction(request):
    cursor = connections['dwh'].cursor()
    cursor.execute("select * from xle.activity")
