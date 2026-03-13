# ①DjangoのView関連

 # Djangoの「テンプレートを表示するだけ」のView（HTMLを返すため）
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, View

 # ログインしていないユーザーをログイン画面へ飛ばすMixin
from django.contrib.auth.mixins import LoginRequiredMixin

 # URLの名前からURLを取得するための関数
from django.urls import reverse_lazy

 # 指定された日付の収支データをJSONに変換してブラウザに返す
from django.http import JsonResponse


# ②便利ツール

 # Python標準ライブラリのカレンダー機能
import calendar

 # 日付で絞り込むために date を使う
from datetime import date

 # 日付を自動で合わせるために使う
from django.utils import timezone

 # DB集計用（合計）
from django.db.models import Sum

 # 日付（DateField）から「日（1〜31）」だけを取り出すための関数
from django.db.models.functions import ExtractDay


# ③自分のアプリのモデルとフォーム

 # households/models.py に定義してある Transaction モデルを使う
from households.models import Transaction

 # form.pyからTransactionFormを読み込む
from .forms import TransactionForm






# --------------------------------------------
# ホーム画面（カレンダー表示）
# --------------------------------------------
class HomeView(LoginRequiredMixin, TemplateView):
    """
    ログイン後に最初に表示されるホーム画面
    ・月カレンダーを表示する
    ・その月の「日別 収入 / 支出 合計」をテンプレに渡す
    """
    # 表示に使うテンプレート
    template_name = "home/home.html"
    
    def get_context_data(self, **kwargs):
        """
        テンプレートに渡すデータ（context）を作るメソッド
        """
        # まずは親クラス（TemplateView）が用意した context を取得
        context = super().get_context_data(**kwargs)
        
        # 取得した日付を表示
        today = timezone.now()
        
        # ============================
        # 表示する年月
        # ============================
        year, month = today.year, today.month

        # ============================
        # カレンダーの枠を作る
        # ============================
        # firstweekday=6 → 日曜始まり
        # 戻り値は「週 × 曜日」の2次元リスト
        # 例：[[1,2,3,4,5,6,7], [8,9,10,11,12,13,14], ...]
        # 月に含まれない日は 0 になる
        cal = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)

        # テンプレートで {{ year }}, {{ month }}, {% for week in calendar %} が使えるようにする
        context.update({"year": year, "month": month, "calendar": cal})

        # ============================
        # この月の収支データを取得
        # ============================
        # ・ログインユーザーのものだけ
        # ・指定した年・月のものだけ
        qs = Transaction.objects.filter(
            user=self.request.user,
            date__year=year,
            date__month=month,
        )

        # ============================
        # 日別「収入合計」を作る
        # ============================
        # 1. tx_type が income のものだけに絞る
        # 2. date から「日」だけを取り出す（ExtractDay）
        # 3. 同じ日の amount を合計（Sum）
        income_by_day = (
            qs.filter(tx_type=Transaction.INCOME)
              .annotate(day=ExtractDay("date"))   # day = 1〜31
              .values("day")
              .annotate(total=Sum("amount"))      # total = その日の収入合計
        )

        # ============================
        # 日別「支出合計」を作る
        # ============================
        expense_by_day = (
            qs.filter(tx_type=Transaction.EXPENSE)
              .annotate(day=ExtractDay("date"))
              .values("day")
              .annotate(total=Sum("amount"))
        )

        # ============================
        # テンプレで使いやすい形に変換
        # ============================
        # QuerySet → 辞書に変換
        # 例：{ 2: 3000, 5: 1200 }
        context["income_map"] = {
            row["day"]: row["total"] for row in income_by_day
        }

        context["expense_map"] = {
            row["day"]: row["total"] for row in expense_by_day
        }

        # 最終的にこの context がテンプレートに渡される
        return context



# ============================
# 日別収支一覧ページ
# ============================

class DayTransactionListView(LoginRequiredMixin, ListView):
    """
    その日（YYYY/MM/DD）の収支(Transaction)だけを一覧表示するView
    ・ログインユーザーのデータだけ
    ・指定日付のデータだけ
    """
    model = Transaction
    template_name = "home/day_list.html"
    context_object_name = "transactions"
    
    def get_queryset(self):
        """
        URLから受け取った year/month/day を使って日付を作り、
        その日付のTransactionだけを取ってくる
        """
        y = int(self.kwargs["year"])
        m = int(self.kwargs["month"])
        d = int(self.kwargs["day"])

        target_date = date(y, m, d)

        return Transaction.objects.filter(
            user=self.request.user,
            date=target_date
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        """
        テンプレで「何日の日別詳細か」を表示できるようにする
        """
        context = super().get_context_data(**kwargs)
        context["year"] = int(self.kwargs["year"])
        context["month"] = int(self.kwargs["month"])
        context["day"] = int(self.kwargs["day"])
        return context

    
# ============================
# 日別収支データのJSON返却View
# ============================
class DayTransactionJsonView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        y = self.kwargs['year']
        m = self.kwargs['month']
        d = self.kwargs['day']
        
        target_date = date(y, m, d)
        # DBから指定した日の自分のデータを取得
        transactions = Transaction.objects.filter(user=request.user, date=target_date).values('id', 'tx_type', 'amount', 'memo')
        # リストを作成
        data = []
        for tx in transactions:
            type_label = "収入" if tx['tx_type'] == Transaction.INCOME else "支出"
            data.append({'id': tx['id'], 'label': f"{type_label}: {tx['amount']}円", 'memo': tx['memo']})
        
        # JSONで返す
        return JsonResponse({'transactions': data})
        


# ============================
# 収支登録ページ
# ============================
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "households/transaction_form.html"
    success_url = reverse_lazy('home:home')
    
    def get_initial(self):
    # URLから日付を取得して初期値にする
        initial = super().get_initial()
        date_str = self.request.GET.get('date')
        if date_str: 
            initial['date'] = date_str
        return initial

    def form_valid(self, form):
    # 保存時にログインユーザーを自動設定
        form. instance. user = self. request. user
        return super().form_valid(form)
            
        

 
    
# ============================
# 収支編集ページ
# ============================
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "households/transaction_form.html"
    success_url = reverse_lazy('home:home')
    
    def get_queryset(self):
    # 自分のデータだけを対象にする
        return Transaction.objects.filter(user=self.request.user)