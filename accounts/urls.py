from django.urls import path
from .views import logout_view, login_view, register_user, user_dashboard, forgot_password, change_password

urlpatterns = [
    path('logout/', logout_view, name="logout"),
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path('dashboard/', user_dashboard, name="user_dashboard"),
    path('forgot-password/', forgot_password, name="forgot_password"),
    path('change-password/', change_password, name="change_password"),
]
