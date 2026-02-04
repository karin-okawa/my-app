from django.urls import path

# households/views.py にあるビュー（CBV）を読み込む
from .views import TransactionListView, TransactionCreateView


# URLの名前空間を households にする
# テンプレートでは {% url 'households:list' %} のように呼び出せるようになる
app_name = "households"

urlpatterns = [
    # 収支一覧ページ（例：/households/）
    path("", TransactionListView.as_view(), name="list"),

    # 収支登録ページ（例：/households/new/）
    path("new/", TransactionCreateView.as_view(), name="new"),
]
