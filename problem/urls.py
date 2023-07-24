from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_lib_page),
    path("<int:question_id>/", views.detail),
]