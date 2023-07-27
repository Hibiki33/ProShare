from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view),
    path('test/', views.test_view),
    path('404', views.not_found_view),
]