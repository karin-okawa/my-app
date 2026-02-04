from django.urls import path
from .views import HomeView

app_name = 'home'

urlpatterns = [
    # ログイン後のトップ(/home/)
    path('', HomeView.as_view(), name='home'),
]
