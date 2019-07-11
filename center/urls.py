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

from center import views, settings
from center import dash_views
from center.dashviews import sports, redcards

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
                  path('dashboard/auction_ms_1', dash_views.dash_auction_2, name='prod_auction_1'),

                  path('dashboard/sport', sports.dash_sports, name='dash_sports'),
                  path('dashboard/sport/<str:date>', sports.dash_sports, name='dash_sports'),
                  path('dashboard/redcards', redcards.dash_redcards, name='dash_redcards'),

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
