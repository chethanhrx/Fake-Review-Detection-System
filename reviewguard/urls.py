from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('users/', include('users.urls')),
    path('reviews/', include('reviews.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]
