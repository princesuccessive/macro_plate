from django.contrib.auth import views as auth_views
from django.urls import path

from apps.users import views as account_views

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='account/login.html',
            redirect_authenticated_user=True,
        ),
        name='account-login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='account-login'
        ),
        name='account-logout',
    ),
    path(
        'profile/',
        account_views.ProfileView.as_view(),
        name='account-profile',
    ),
]
