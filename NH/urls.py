"""NH URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("r'^login/$'", views.login_view, name="login_view"),
    path("", views.main_index, name="main_index"),
    path("logout", views.logout_view, name="logout_view"),
    path("inventory/", include("inventory.urls")),
    path("users", views.user_list, name="user_list"),
    path("development", views.development, name="development"),
    path("user_info", views.user_info, name="user_info"),
]