from django.urls import path
from .views import (
    HomeView, 
    DayTransactionListView
)


app_name = 'home'

urlpatterns = [
    # ログイン後のトップ(/home/)
    path('', HomeView.as_view(), name='home'),
    
    # ✅ 日別詳細（例：/home/2026/2/1/）
    path("<int:year>/<int:month>/<int:day>/", DayTransactionListView.as_view(), name="day_detail"),

]
