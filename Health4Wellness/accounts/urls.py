from django.contrib import admin
from django.contrib import auth
from django.urls import include, path
from . import views

app_name = 'accounts_app'
urlpatterns = [
    path('register', views.register, name='register'),
    path('<user_id>/profile', views.show_profile, name='profile'),
    path('<user_id>/update', views.update_profile, name='update'),
]