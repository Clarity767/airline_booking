from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = "flights"

urlpatterns = [
    path("", views.home, name="home"),
    path("flights/", views.flight_list, name="flight_list"),
    path("flights/<int:pk>/", views.flight_detail, name="flight_detail"),
    path(
        "bookings/<int:pk>/",
        views.booking_confirmation,
        name="booking_confirmation",
    ),
        path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="flights/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="flights:home"),
        name="logout",
    ),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/password/", views.change_password, name="change_password"),
        path(
        "bookings/<int:pk>/cancel/",
        views.cancel_booking,
        name="cancel_booking",
    ),

]