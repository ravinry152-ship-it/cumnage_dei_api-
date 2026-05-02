from django.urls import path
from. import views
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('api/register/', views.Register.as_view(), name='register'),
    path('api/login/', views.Login.as_view(), name='login'),
    path('api/google/login/', views.GoogleLogin.as_view(), name='google_login'),
    path('api/setup-system/', views.SetupSystem.as_view(), name='setup_system'),
    path('api/detail_setup_system/<int:pk>/', views.SetupSystemDetail.as_view(), name='detail_setup_system'),
    path('api/userdata/', views.UserData.as_view(), name = 'userdata'),
    path('api/detail_userdata/<int:pk>/', views.UserDataDetail.as_view(), name = 'detail_userdata'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')


]
