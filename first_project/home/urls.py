from django.urls import path
from .views import (
    HomeView, 
    DayTransactionListView,
    DayTransactionJsonView,
    TransactionCreateView,
    TransactionUpdateView,
    TransactionDeleteView,
    HouseholdSwitchView,
    HouseholdCreateView,
    HouseholdDeleteView,
    HouseholdUpdateView,
    HouseholdInviteView,
    HouseholdJoinView,
    GraphView,
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
    # 収支削除
    path('delete/<int:pk>/', TransactionDeleteView.as_view(), name='transaction_delete'),
    # 家計簿切り替え
    path('household/switch/', HouseholdSwitchView.as_view(), name='household_switch'),
    # 家計簿新規作成
    path('household/create/', HouseholdCreateView.as_view(), name='household_create'),
    # 家計簿削除
    path('household/delete/', HouseholdDeleteView.as_view(), name='household_delete'),
    # 家計簿名編集
    path('household/update/', HouseholdUpdateView.as_view(), name='household_update'),
    # 招待リンク発行
    path('household/invite/', HouseholdInviteView.as_view(), name='household_invite'),
    # 招待リンクで家計簿に参加するURL
    path('household/join/<str:token>/', HouseholdJoinView.as_view(), name='household_join'),
    # グラフ画面
    path('graph/', GraphView.as_view(), name='graph'),
    # 年月指定のグラフ画面
    path('graph/<int:year>/<int:month>/', GraphView.as_view(), name='graph_with_month'),
]
