from django.urls import path
from .views import (
    RegistUserView, UserLoginView, UserLogoutView
)

app_name = 'accounts'
urlpatterns = [
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]

