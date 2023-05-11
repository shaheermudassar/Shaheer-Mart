from django.urls import path, include
from userauths import views
from core.views import create_profile

app_name = 'userauths'

urlpatterns = [
    path("signup", views.register_views, name="signup"),
    path("signin", views.login_view, name="signin"),
    path("signout", views.logout_view, name="signout"),
    path("change_password", views.change_password, name="change_password"),
    path("create-profile/", create_profile, name="create-profile")
]


