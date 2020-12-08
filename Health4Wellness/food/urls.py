from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<name>/', views.detail, name='detail'),
    path('compare/', views.compare_search, name='compare'),
    path('compare/<name1>/<name2>/', views.compare, name='compare'),
]
