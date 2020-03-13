from django.urls import path
from . import views
app_name = 'userinfo'
urlpatterns = [
    path('detail/', views.UserInfoView.as_view(), name='detail'),
    path('crop-upload-image/', views.crop_upload_handler, name='crop_upload_image'),
    path('user-signup-validate', views.user_signup_validate, name='user_signup_validate'),
]
# app_name = 'userinfo'
# urlpatterns = [
#     path('login/', views.user_login, name='login'),
#     path('logout/', views.user_logout, name='logout'),
#     path('register/', views.user_register, name='register'),
#     path('delete/<int:id>/', views.user_delete, name='delete'),
#     path('edit/<int:id>/', views.profile_edit, name='edit'),
#
# ]