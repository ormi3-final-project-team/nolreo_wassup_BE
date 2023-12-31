from django.urls import path

from . import views

app_name = 'pick'

urlpatterns = [
    path('lodging/', views.lodging_pick, name='lodging_pick_cl'),
    path('lodging/<int:pk>/', views.lodging_pick, name='lodging_pick_d'),
    path('bus/', views.bus_pick, name='bus_pick_cl'),
    path('bus/<int:pk>/', views.bus_pick, name='bus_pick_d'),
    path('train/', views.train_pick, name='train_pick_cl'),
    path('train/<int:pk>/', views.train_pick, name='train_pick_d'),
    path('rental_car/', views.rental_car_pick, name='rental_car_pick_cl'),
    path('rental_car/<int:pk>/', views.rental_car_pick, name='rental_car_pick_d'),
    path('', views.pick_list, name='pick_list'),
]