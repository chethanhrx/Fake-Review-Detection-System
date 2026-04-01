from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.admin_register, name='admin_register'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('reviews/', views.admin_reviews, name='admin_reviews'),
    path('reviews/flag/<int:review_id>/', views.toggle_flag, name='toggle_flag'),
    path('reviews/override/<int:review_id>/', views.override_result, name='override_result'),
    path('reviews/delete/<int:review_id>/', views.admin_delete_review, name='admin_delete_review'),
    path('users/', views.admin_users, name='admin_users'),
]
