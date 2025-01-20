"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from schoolapp.views import auth_check


admin.site.site_header = ' '
admin.site.site_title = 'ADMIN PANEL'
admin.site.index_title = 'EVIKA SCHOOL'

urlpatterns = [
    path('evika-school/login/', auth_views.LoginView.as_view(next_page='main-page'), name='login_view'),
    path('evika-school/logout/', auth_views.LogoutView.as_view(next_page='login_view'), name='logout_view'),
    path('evika-school/check-auth/', auth_check, name='auth-check'),
    path('', lambda request: redirect('/evika-school/', permanent=False)),
    path('admin/', admin.site.urls),
    path('evika-school/', include('schoolapp.urls'))
]
