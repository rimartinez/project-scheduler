from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    # Schedule CRUD
    path('', views.ScheduleListView.as_view(), name='list'),
    path('create/', views.ScheduleCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ScheduleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ScheduleUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='delete'),
    
    # Schedule Actions
    path('<int:pk>/submit/', views.ScheduleSubmitView.as_view(), name='submit'),
    path('<int:pk>/approve/', views.ScheduleApproveView.as_view(), name='approve'),
    path('<int:pk>/reject/', views.ScheduleRejectView.as_view(), name='reject'),
    
    # Views
    path('calendar/', views.ScheduleCalendarView.as_view(), name='calendar'),
    path('table/', views.ScheduleTableView.as_view(), name='table'),
    path('approvals/', views.ScheduleApprovalsView.as_view(), name='approvals'),
    
    # HTMX endpoints
    path('calendar/month/<int:year>/<int:month>/', views.CalendarMonthView.as_view(), name='calendar_month'),
    path('table/data/', views.ScheduleTableDataView.as_view(), name='table_data'),
]
