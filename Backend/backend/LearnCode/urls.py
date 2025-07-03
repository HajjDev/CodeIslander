from django.urls import path
from .views import register, user_login, user_logout, user_home, activate, reset_password, reset_confirmation
from . import views
urlpatterns = [
    path('', user_home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path("password_reset", views.reset_password, name="password_reset"),
    path('reset/<uidb64>/<token>', views.reset_confirmation, name='password_reset_confirm'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]