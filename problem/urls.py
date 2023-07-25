from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_lib_page),
    path("<int:id>/", views.detail),

    path('problem_upload/', views.problem_upload_page),
]