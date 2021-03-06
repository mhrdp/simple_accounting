from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls import url

from .views import LoginView, user_setting
from .forms import ResetPasswordForm

from . import views as user_views

urlpatterns = [
    path('', user_views.index, name='index'),
    
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('company/profile/', user_views.company_profile, name='profile'),
    path('company/profile/details/edit/', user_views.company_profile_edit, name='edit'),
    path('company/profile/user/edit', user_views.user_profile_edit, name='user_edit'),
    path('company/profile/change-password/', user_views.user_change_password, name='change_password'),
    path('logout/', user_views.user_logout, name='logout'),
    #path('settings/', user_views.user_setting_ajax, name='setting'),
    path('company/profile/user/configurations/', user_views.user_setting, name='conf'),

    # Reset password
    path(
        'password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='user/reset_password.html',
            form_class=ResetPasswordForm,
        ), 
        name='reset_password'
        ),
    path(
        'password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/reset_password_done.html',
        ), 
        name='password_reset_done'
        ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user/reset_password_confirm.html',
        ), 
        name='password_reset_confirm'
        ),
    path(
        'password-reset/complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/reset_password_complete.html',
        ), 
        name='password_reset_complete'
        ),
]