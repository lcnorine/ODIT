"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path  #, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('',  views.index),
    path('index.html', views.index),
    path('submit.html', views.submit),
    path('viewissues.html', views.viewissues),
    path('viewmyissues.html', views.viewmyissues),
    path('viewmysubmittedissues.html', views.viewmysubmittedissues),
    path('viewissues/assign/<int:issue_id>', views.self_assign),
    path('resolve/<int:id>', views.resolve_ticket),
    path('editticket/<int:id>', views.edit_ticket),
    path('aboutodit.html', views.about),
    path('profile.html', views.profile_page),
    path('profile/edit.html', views.edit_profile),
    path('profile/become_technician', views.become_technician),
    path('viewtechnicians.html', views.view_technicians),
    path('viewprofile/<int:user_id>', views.view_profile),
    path('editreview/<int:id>', views.edit_review),
    path('login/', auth_views.LoginView.as_view()),
    path('register/', views.register),
    path('logout/', views.logoff)
]
