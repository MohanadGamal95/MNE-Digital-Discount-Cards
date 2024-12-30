from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "Discount_Card"

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>', views.activate_account, name='activate'),
    path('resend_activation/', views.resend_activation, name='resend_activation'),
    path('email_not_verified/', views.email_not_verified, name='email_not_verified'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('download_card/<int:member_id>/', views.download_card_pdf, name='download_card_pdf'),
    path('medical_network/', views.medical_network, name='medical_network'),
    path("logout", views.logout_view, name="logout"),
    # Password reset URLs using Django default
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_sent'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #Payment 
    path('payment', views.payment, name='payment'),
    path('api/providers', views.fetch_providers, name='fetch_providers'),
    path('api/filters', views.fetch_filters, name='fetch_filters'),
    path('api/filter_results', views.fetch_filtered_results, name='fetch_filtered_results')
]

