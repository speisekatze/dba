from django.urls import path

from . import views

app_name = 'dba'
urlpatterns = [
    path('', views.DbListView.as_view(), name='index'),
    path('dba/', views.DbListView.as_view(), name='index'),
    path('newdb/success/<int:dbtid>', views.NewDBSuccess.as_view(), name='newdbsuccess'),
    path('newdb/<str:host>', views.NewDBView.as_view(), name='newdb'),
    path('newdb/<str:host>/<str:instance>', views.NewDBView.as_view(), name='newdb'),
    
]
