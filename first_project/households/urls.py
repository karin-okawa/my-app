from django.urls import path
from . import views
from .views import (
    TransactionListView, TransactionCreateView, DayTransactionsJsonView, 
    TransactionUpdateView, CategoryListView, CategoryCreateView, 
    CategoryUpdateView, CategoryDeleteView, CategoryReorderView,
    CategoryColorView
)


# URLの名前空間を households にする
# テンプレートでは {% url 'households:list' %} のように呼び出せるようになる
app_name = "households"

urlpatterns = [
    # 収支一覧ページ（例：/households/）
    path("", TransactionListView.as_view(), name="list"),

    # 収支登録ページ（例：/households/new/）
    path("new/", TransactionCreateView.as_view(), name="create"),
   
    # 指定した「年・月・日」の収支データをJSONで返すAPI用URL
    # 例: /households/api/day/2026/2/1/ 
    # → DayTransactionsJsonView が実行され、
    #   その日の収支データをモーダル表示用に返す
    path("api/day/<int:year>/<int:month>/<int:day>/", DayTransactionsJsonView.as_view(), name="day_api"),

    # 編集用のパスを追加（<int:pk> でどの収支かを指定）
    path('transaction/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),

    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/new/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    # 並び替え結果をサーバーに保存するAPI用URL
    path('categories/reorder/', views.CategoryReorderView.as_view(), name='category_reorder'),
    # カテゴリーの色選択ページ
    path('categories/<int:pk>/color/', views.CategoryColorView.as_view(), name='category_color'),
]
