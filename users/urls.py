from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("login", views.login_view, name="login"),
    # path("login/", views.user_login, name="login"),
    # path("logout", views.logout_view, name="logout")

    # url-адреса входа и выхода
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
