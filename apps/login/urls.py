from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("guest/", views.guest_login_view, name="guest_login"),
]
