from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsIndexView.as_view(), name='index'),
    path('employee/', views.EmployeeReportsView.as_view(), name='employee'),
    path('client/', views.ClientReportsView.as_view(), name='client'),
    path('supervisor/', views.SupervisorReportsView.as_view(), name='supervisor'),
    path('export/', views.ExportReportsView.as_view(), name='export'),
]
