from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('compare/<name1>/<name2>/', views.compare, name='compare'),
    path('<name>/', views.detail, name='detail'),
]
