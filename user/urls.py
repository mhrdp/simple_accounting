from django.urls import path
from .views import LoginView

from . import views as user_views

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('company/profile/', user_views.company_profile, name='profile'),
    path('company/profile/edit', user_views.company_profile_edit, name='edit'),
    path('logout/', user_views.user_logout, name='logout')
]