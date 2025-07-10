from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('LearnCode/', include('LearnCode.urls')),
    path('accounts/', include('allauth.urls')),

]