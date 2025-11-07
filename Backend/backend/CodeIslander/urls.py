from django.urls import path
from CodeIslander.views import welcome, exercise_page, qcm_detail, theory_detail, register, run_code_secure, user_login, user_logout, user_home, verify, activate, reset_password, reset_confirmation, profile_view, reset_email, reset_username, activateChangeEmail, startTotp, enableTotp, stopTotp, disableTotp, map1, vip_funct, update_funct, support_funct, map2

urlpatterns = [
    path('', welcome, name='welcome'),
    path('home/', user_home, name='home'),
    path('map1/', map1, name='map1'),
    path('map2/', map2, name='map2'),
    path('vip/', vip_funct, name='vip'),
    path('support/', support_funct, name='support'),
    path('updates/', update_funct, name='updates'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('login/verify/', verify, name="verify"),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/start-totp/', startTotp, name='enable_totp' ),
    path('profile/verify-totp/', enableTotp, name='verify_totp'),
    path('profile/stop-totp', stopTotp, name='stop_totp'),
    path('profile/disable-totp/', disableTotp, name="disable_totp"),
    path("password_reset", reset_password, name="password_reset"),
    path('reset/<uidb64>/<token>', reset_confirmation, name='password_reset_confirm'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('activateChange/<uidb64>/<token>', activateChangeEmail, name='activateEmailChange'),
    path('email_reset/', reset_email, name='email_reset'),
    path('username_reset/', reset_username, name='username_reset'),
    path('runner/<int:exercise_id>/', exercise_page, name='exercise_page'),
    path('run-code-secure/<int:exercise_id>/', run_code_secure, name='run_code_secure'),
    path('qcm/<int:qcm_id>/', qcm_detail, name='qcm_detail'),
    path('theory/<int:theory_id>/', theory_detail, name='theory_detail')
]