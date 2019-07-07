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

urlpatterns = [
                  path('', include('social_django.urls', namespace='social')),
                  path('logout/', views.logout, name='logout'),
                  path('admin/', admin.site.urls),
                  path('', views.dashboards, name='home'),
                  path('dashboards/', views.dashboards, name='dashboards'),
                  path('reports/', views.reports, name='reports'),
                  path('attendance/', views.attendance_dtrace, name='attendance'),
                  path('test_report/', views.run_report, name='test_report'),
                  path('demo/', views.demo, name='demo'),
                  path('demo_timetable/', views.demo_timetable, name='demo_timeteble'),
                  path('demo_test/', views.demo_test, name='demo_test')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
