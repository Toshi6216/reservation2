from django.urls import path
from accounts import views

urlpatterns = [
    path('userprofile/<int:pk>/', views.ProfileView.as_view(), name='userprofile'),
    path('userprofile_form/<int:pk>/', views.ProfileEditView.as_view(), name='userprofile_form'),

]