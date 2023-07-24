from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_lib_page),
    path("<int:id>/", views.detail),

    path('upload_problem/', views.upload_problem_page),
]