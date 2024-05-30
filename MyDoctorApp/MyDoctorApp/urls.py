"""
URL configuration for MyDoctorApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("appointments", views.appointments, name="appointments"),
    path("availability", views.availability_view, name="availability"),
    path('availability/delete/<int:availability_id>/', views.delete_availability_view, name='delete_availability'),
    path("chats", views.chats, name="chats"),
    path('chats/<int:chat_id>/', views.chat, name='chat'),
    path('chats/new/', views.chat, name='new_chat'),
    path('chats/delete/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('all-doctors/', views.doctors, name='all_doctors'),
    path('my-doctors/', views.doctors, name='my_doctors'),
    path('doctor/<int:doctor_id>/', views.doctor, name='doctor'),
    path('patient/<int:patient_id>/', views.patient, name='patient'),
    path('add_to_saved_users/<int:user_to_save_id>/', views.add_to_saved_users, name='add_to_saved_users'),
    path('remove_from_saved_users/<int:user_to_remove_id>/', views.remove_from_saved_users, name='remove_from_saved_users'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)