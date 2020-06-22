from django.urls import path

from . import views

app_name = 'passwd'
urlpatterns = [
    path('', views.PasswdView.as_view(), name='index'),
    path('ergebniss', views.PasswdView.as_view(), name='ergebniss'),
]
