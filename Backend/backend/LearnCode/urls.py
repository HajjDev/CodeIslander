from django.urls import path
from LearnCode.views import welcome, register, user_login, user_logout, user_home, activate, reset_password, reset_confirmation, profile_view, reset_email, reset_username

urlpatterns = [
    path('', welcome, name='welcome'),
    path('home/', user_home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile_view, name='profile'),
    path("password_reset", reset_password, name="password_reset"),
    path('reset/<uidb64>/<token>', reset_confirmation, name='password_reset_confirm'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('email_reset/', reset_email, name='email_reset'),
    path('username_reset/', reset_username, name='username_reset'),

]