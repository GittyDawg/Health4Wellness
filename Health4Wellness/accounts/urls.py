from django.contrib import admin
from django.contrib import auth
from django.urls import include, path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register', views.register, name='register'),
    path('<int:user_id>/profile', views.show_profile, name='profile'),
    path('<int:user_id>/update', views.update_profile, name='update'),
    path('<int:user_id>/<int:log_id>', views.dietlog, name='log'),
    path('<int:user_id>/<int:log_id>/updatelog', views.update_dietlog, name='update_dietlog')
]