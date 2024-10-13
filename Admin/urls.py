from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_view, name='adminlogin'),
    path('signup/', views.admin_signup_view, name='adminsignup'),
    path('dashboard/', views.admin_dashboard_view, name='admindashboard'),
    path('logout/', views.admin_logout_view, name='adminlogout'),
    path('graphs/', views.admin_graphs, name='admin_graphs'),
    path('branches/', views.admin_branches, name='admin_branches'),
    path('managers/', views.admin_managers, name='admin_managers'),
]
