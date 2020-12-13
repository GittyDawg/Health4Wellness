from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search_fda/', views.search_fda, name='search_fda'),
    path('search_fda_list/', views.search_fda_list, name='search_fda_list'),
    path('search_fda_details/', views.search_fda_details, name='search_fda_details'),
    path('compare/', views.compare, name='compare'),
    path('compare_search/', views.compare_search, name='compare_search'),
    #path('added_food/<meal>/<name>/', views.added_food, name='added_food'),
    path('<name>/', views.detail, name='detail'),
    path('<int:meal_id>/view', views.view_meal, name='view_meal'),
    path('<int:meal_id>/update', views.update_meal, name='update_meal'),
    path('add/<int:food_id>', views.add_food_to_meal, name='add_food'),
]
