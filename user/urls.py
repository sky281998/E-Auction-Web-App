from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('message/', views.message_view, name='message'),
    path('write/<int:pk>/', views.write_to, name='write_to')
]