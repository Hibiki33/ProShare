from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view),
    path('login/', views.login_page),
    path('register/', views.register_page)
]
