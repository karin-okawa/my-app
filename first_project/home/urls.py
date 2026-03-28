from django.urls import path
from .views import (
    HomeView, 
    DayTransactionListView,
    DayTransactionJsonView,
    TransactionCreateView,
    TransactionUpdateView,
)

app_name = 'home'

urlpatterns = [
    # カレンダーのトップ画面
    # /home/ だけでも、/home/2026/3/ のように年月指定してもHomeViewが開くようにする
    path('', HomeView.as_view(), name='home'),
    path('<int:year>/<int:month>/', HomeView.as_view(), name='home_with_month'),
    
    # 日別詳細（例: /home/2026/2/10/）
    path('<int:year>/<int:month>/<int:day>/', DayTransactionListView.as_view(), name='day_detail'),

    # モーダルでデータを読み込む用
    path('day-json/<int:year>/<int:month>/<int:day>/', DayTransactionJsonView.as_view(), name='day_json'),

    # 新規登録画面
    path('create/', TransactionCreateView.as_view(), name='transaction_create'),
   
    # 編集画面
    path('update/<int:pk>/', TransactionUpdateView.as_view(), name='transaction_update'),

]
