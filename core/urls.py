from django.urls import path
from . import views
from .views import RegisterUser, LoginUser

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('c-poll/', views.create_poll, name='c-poll'),
    path('c-vote/<str:slug>/<str:slugx>/', views.caste_vote, name='c-vote'),
    path('cn-vote/<str:slug>/<str:slugx>/<int:pk>/',
         views.count_vote, name='cn-vote'),
]
