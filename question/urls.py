from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_lib_page),
]