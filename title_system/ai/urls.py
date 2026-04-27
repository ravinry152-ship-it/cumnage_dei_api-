from django.urls import path
from. import views

urlpatterns = [
    path('json/',views.DocumentUploadView.as_view(), name='json'),
]