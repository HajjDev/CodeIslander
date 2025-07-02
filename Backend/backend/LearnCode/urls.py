from django.urls import path
from .views import register, user_login, user_logout, user_home
from . import views
urlpatterns = [
    path('', user_home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]