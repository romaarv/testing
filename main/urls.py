from django.urls import path

from .views import *


app_name = 'main'

urlpatterns = [
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/pasword/change/', TestingPasswordChangeView.as_view(), name='pasword_change'),
    path('accounts/login/', TestingLoginView.as_view(), name='login'),
    path('accounts/logout', TestingLogoutView.as_view(), name='logout'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]