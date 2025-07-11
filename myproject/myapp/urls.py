from django.urls import path
from . import views

#urlpatterns = [
#    path('register/', views.register_student, name='register_student'),
#    path('success/', views.success, name='success'),
#    path('students/', views.list_students, name='list_students'),
#]
#manually added 
from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/admin/login/', views.admin_login_view, name='admin_login'),
    path('dashboard/admin/logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/admin/approve/<int:app_id>/', views.admin_approve_application, name='admin_approve_application'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/gatepassform/', views.gatepass_form_view, name='gatepass_form'),
    path('dashboard/applications/', views.applications_view, name='applications'),
    path('dashboard/changepassword/', auth_views.PasswordChangeView.as_view(template_name='change_password.html'), name='change_password'),
    path('dashboard/changepassword/done/', auth_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html'), name='password_change_done'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]