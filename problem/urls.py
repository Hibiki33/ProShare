from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_main_page),
    path("<int:id>/", views.problem_detail_page),
    path('create/', views.problem_create_page),
    path('upload/', views.problem_upload_page),
    path('set/', views.problem_set_list_page),
    path('set/<int:set_id>/', views.problem_set_detail_page),
    # path('set/<int:set_id>/modify/', ),
    # path('set/<int:set_id>/modify/add/', ),
    # path('set/<int:set_id>/result/', ),
    path('set/create/', views.problem_set_create_page),
    # path('set/create/add', ),
]