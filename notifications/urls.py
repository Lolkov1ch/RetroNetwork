from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('json/', views.notifications_json, name='notifications_json'),
    path('mark-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
]
