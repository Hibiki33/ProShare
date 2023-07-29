from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page),
    path('change_password/', views.change_password_page),
    path('edit/', views.edit_page),
    path('login/', views.login_page),
    path('logout/', views.logout_page),
    path('register/', views.register_page),
    path('group/<group_name>', views.group_detail_page),
    path('group/search/', views.group_search_page),
    path('punlum/', views.punlum_page),
]
