from django.urls import path
from . import views
from .views import RegisterUser, LoginUser, Dashboard

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('dashboard/<str:slug>/', Dashboard.as_view(), name='dashboard'),
    path('create-poll/<str:slug>/', views.create_poll, name='c-poll'),
    path('edit-poll/<str:slug>/<str:slugx>/', views.edit_poll, name='e-poll'),
    path('c-vote/<str:slug>/<str:slugx>/', views.caste_vote, name='c-vote'),
    path('cn-vote/<str:slug>/<str:slugx>/<str:slugz>/',
         views.count_vote, name='cn-vote'),
    path('gen-cert/<str:slug>/<str:slugx>/',
         views.download_certificate, name="print_cert")
]
