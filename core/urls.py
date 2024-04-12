from django.urls import path
from . import views
from .views import RegisterUser, LoginUser, Dashboard

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('dashboard/<str:slug>/', Dashboard.as_view(), name='dashboard'),
    path('create-poll/<str:slug>/', views.create_poll, name='c-poll'),
    path('edit-poll/<str:slug>/<int:pk>/',
         views.edit_poll, name='e-poll'),
    path('poll/<str:slug>/<str:title>/',
         views.caste_vote, name='c-vote'),
    path('cn-vote/<str:slug>/<str:slugx>/<str:slugz>/<int:pk>/',
         views.count_vote, name='cn-vote'),
    path('gen-cert/<str:slug>/<int:pk>/',
         views.download_certificate, name="print_cert"),
    path('voted/', views.thanks_for_voting, name='voted'),
]
