from django.urls import path
from . import views
from .views import RegisterUser, LoginUser, Dashboard

urlpatterns = [
    path('', views.home, name='home'),
    path('buy_credit/', views.buy_credit, name='buy_credit'),
    path('contact/', views.contact, name='contact'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('dashboard/<str:slug>/', Dashboard.as_view(), name='dashboard'),
    path('create-poll/<str:slug>/', views.create_poll, name='c-poll'),
    path('edit-poll/<str:slug>/<int:pk>/',
         views.edit_poll, name='e-poll'),
    path('poll/<str:slug>/<str:title>/',
         views.caste_vote, name='c-vote'),
    path('cn-vote/<str:slug>/<int:pk>/<str:slugz>/',
         views.count_vote, name='cn-vote'),
    path('gen-cert/<str:slug>/<int:pk>/',
         views.download_certificate, name="print_cert"),
    path('voted/', views.thanks_for_voting, name='voted'),
    path('random-award/<str:slug>/',
         views.generate_random_certificate, name='random-cert'),
    path('ld-rank/<str:slug>/<str:month>/<str:action>/<str:nominee_name>/',
         views.leaderboard_rank, name='leaderboard_rank'),
    path('add-ld/<str:slug>/<str:month>/',
         views.add_leaderboard, name='add_leaderboard'),
    path('gen-award/<str:slug>/<int:pk>/',
         views.download_award, name="print_badge"),
    path('signout/', views.signout, name='signout'),
]
