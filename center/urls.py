"""sit_center URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from center import views, settings
from center import dash_views
from center.dashviews import sports, redcards, auction, aim, dtrace

urlpatterns = [
                  path('', include('social_django.urls', namespace='social')),
                  path('logout/', views.logout, name='logout'),
                  path('admin/', admin.site.urls),
                  path('', views.dashboards, name='home'),
                  path('dashboards/', views.dashboards, name='dashboards'),
                  path('reports/', views.reports, name='reports'),
                  path('attendance/', views.attendance_dtrace, name='attendance'),

                  # PROD BOARDS
                  path('dashboard/all', dash_views.dash_all, name='prod_all'),
                  path('dashboard/auctions', dash_views.dash_auctions, name='prod_auction'),
                  path('dashboard/auction_one', dash_views.dash_auction_one, name='prod_auction_1'),
                  path('dashboard/auction_lab_1', dash_views.dash_auction_labs_1, name='prod_auction_1'),
                  path('dashboard/auction_ms_1', dash_views.dash_auction_2, name='prod_auction_ms_1'),
                  path('dashboard/auction_ms_2', dash_views.dash_auction_3, name='prod_auction_ms_2'),
                  path('dashboard/auction_ms_3', dash_views.dash_auction_4, name='prod_auction_ms_2'),

                  path('dashboard/auction', auction.dash_auction_progress, name='prod_auction_all'),
                  path('dashboard/auction/<str:date>', auction.dash_auction_progress, name='prod_auction_all'),
                  path('dashboard/sport', sports.dash_sports, name='dash_sports'),
                  path('dashboard/sport/<str:date>', sports.dash_sports, name='dash_sports'),
                  path('dashboard/redcards', redcards.dash_redcards, name='dash_redcards'),
                  path('dashboard/auction_result', auction.dash_auction_result, name='dash_auction_result'),
                  path('dashboard/auction_result/<str:date>', auction.dash_auction_result, name='dash_auction_result_by_id'),
                  path('dashboard/aim', aim.dash_aim, name='dash_aim'),
                  path('dashboard/dtrace', dtrace.dash_dtrace, name='dash_trace'),

                  path('dashboard/feedback', RedirectView.as_view(
                      url='https://app.powerbi.com/view?r=eyJrIjoiOGQyNmU5MGEtNmVmMC00OTRlLWIzZDAtYWI4ZjYzZDcxODcxIiwidCI6ImIzMzQ2YTIwLTU1YzUtNGU0Yy04ZGM0LTBmMThjNjU0MTE3MSIsImMiOjl9',
                      permanent=False), name='feedback_ext'),

                  # TEST BOARDS
                  path('test_report/', views.run_report, name='test_report'),
                  path('demo/', views.demo, name='demo'),
                  path('demo_timetable/', views.demo_timetable, name='demo_timeteble'),
                  path('demo_feedback/', views.demo_feedback, name='demo_feedback'),
                  path('demo_test/', views.demo_test, name='demo_test'),
                  path('test_auction/', views.test_auction, name='test_auction'),
                  path('test_all/', views.test_all, name='test_auction')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
