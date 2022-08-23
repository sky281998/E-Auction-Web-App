from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_upcoming, name='show_upcoming'),
    path('ended/', views.show_ended, name='show_ended'),
    path('add/', views.add, name='add_auction'),
    path('details/<int:pk>/', views.details, name='show_details'),
    path('buy/<int:pk>/', views.buy, name='buy_item'),
    path('search/<str:search_text>/', views.search_result, name='search_result')
]