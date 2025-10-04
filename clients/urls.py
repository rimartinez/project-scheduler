from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.ClientListView.as_view(), name='list'),
    path('my-schedules/', views.ClientScheduleView.as_view(), name='my_schedules'),
    path('reports/', views.ClientReportsView.as_view(), name='reports'),
]
