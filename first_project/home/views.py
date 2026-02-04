# Djangoの「テンプレートを表示するだけ」のView（ホーム画面などに使う）
from django.views.generic import TemplateView

# ログイン必須にするMixin（未ログインならLOGIN_URLへ飛ばす）
from django.contrib.auth.mixins import LoginRequiredMixin

# 汎用クラスベースビュー（一覧表示 / 新規作成）
from django.views.generic import ListView, CreateView

# URLの名前（namespace:name）からURLを作るためのもの
from django.urls import reverse_lazy

# Python標準のカレンダーを使うため
import calendar

# households/models.py にある Transaction を読み込む
from households.models import Transaction


# --------------------------------------------
# ① ホーム画面（カレンダーを表示するページ）
# --------------------------------------------
class HomeView(LoginRequiredMixin, TemplateView):
    """
    ログイン後に見せたいホーム画面（カレンダー）
    ・まずは固定で年月（2026年2月）を表示
    ・テンプレートにカレンダー用のデータ（週×曜日）を渡す
    """
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡す値（context）を追加する
        """
        # まずは親クラスが用意するcontextを取得
        context = super().get_context_data(**kwargs)

        # とりあえず固定で 2026年2月（あとで動的にする）
        year = 2026
        month = 2

        # 週 × 曜日の2次元リストを作る
        # 日曜始まりのカレンダーを作る（6 = 日曜日）
        cal = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)

        # テンプレートで使えるように context に入れる
        context["year"] = year
        context["month"] = month
        context["calendar"] = cal

        return context


# --------------------------------------------
# ② 収支一覧（ログインユーザーのTransactionだけ表示）
# ※「homeアプリ内で一覧を出す」暫定版の置き場所
#   将来的には households/views.py に移すのが自然
# --------------------------------------------
class TransactionListView(LoginRequiredMixin, ListView):
    """
    Transaction（収支）の一覧画面
    ・ログインしているユーザーのデータだけ表示する
    """
    model = Transaction
    template_name = "transactions/list.html"
    context_object_name = "transactions"

    def get_queryset(self):
        """
        表示するデータを「ログインユーザーのものだけ」に絞る
        """
        return Transaction.objects.filter(user=self.request.user)


# --------------------------------------------
# ③ 収支登録（ログインユーザーとして保存）
# --------------------------------------------
class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    Transaction（収支）の新規作成画面
    ・フォームから登録
    ・保存時に user を自動で入れる
    """
    model = Transaction
    fields = ["date", "tx_type", "amount", "memo", "image"]
    template_name = "transactions/form.html"

    # ✅ ここはあなたのURL構成に合わせて変えてOK
    # 迷うなら一旦ホームに戻すのが安全
    # success_url = reverse_lazy("home:home")
    success_url = reverse_lazy("home:home")

    def form_valid(self, form):
        """
        保存前に user をログインユーザーにセット
        """
        form.instance.user = self.request.user
        return super().form_valid(form)
