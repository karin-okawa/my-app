from django.urls import path

# households/views.py にあるビュー（CBV）を読み込む
from .views import TransactionListView, TransactionCreateView, DayTransactionsJsonView


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

]
