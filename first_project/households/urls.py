from django.urls import path  # URLパターン定義関数のインポート
from .views import (  # このアプリ内のビュークラスのインポート
    TransactionListView, TransactionCreateView, DayTransactionsJsonView,
    TransactionUpdateView, CategoryListView, CategoryCreateView,
    CategoryUpdateView, CategoryDeleteView, CategoryReorderView,
    CategoryColorView,
)

# URLの名前空間（テンプレートから 'households:list' のように参照する際に使用）
app_name = "households"

urlpatterns = [
    # 収支一覧ページ
    path("", TransactionListView.as_view(), name="list"),
    # 収支登録ページ
    path("new/", TransactionCreateView.as_view(), name="create"),
    # 指定した日の収支データをJSON形式で返すAPI用URL（モーダル表示用）
    path("api/day/<int:year>/<int:month>/<int:day>/", DayTransactionsJsonView.as_view(), name="day_api"),
    # 収支編集ページ（<int:pk>でどの収支かを指定）
    path('transaction/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_edit'),
    # カテゴリー一覧ページ
    path('categories/', CategoryListView.as_view(), name='category_list'),
    # カテゴリー新規作成ページ
    path('categories/new/', CategoryCreateView.as_view(), name='category_create'),
    # カテゴリー編集ページ
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    # カテゴリー削除処理
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    # カテゴリーの並び替え結果をサーバーに保存するAPI用URL
    path('categories/reorder/', CategoryReorderView.as_view(), name='category_reorder'),
    # カテゴリーの色選択ページ
    path('categories/<int:pk>/color/', CategoryColorView.as_view(), name='category_color'),
]