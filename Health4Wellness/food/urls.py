from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('compare/', views.compare, name='compare'),
    path('compare_search/', views.compare_search, name='compare_search'),
    path('<name>/', views.detail, name='detail'),
]
