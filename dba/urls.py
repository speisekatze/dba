from django.urls import path

from . import views

app_name = 'dba'
urlpatterns = [
    path('', views.dblistView.as_view(), name='index'),
    path('newdb/<str:host>', views.NewDBView.as_view(), name='newdb'),
    path('newdb/<str:host>/<str:instance>', views.NewDBView.as_view(), name='newdb'),
]
