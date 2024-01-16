from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),
    path('mapsfilter/', views.maps_filter, name='maps_filter'),
]
