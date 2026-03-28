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
from households.forms import TransactionForm






# --------------------------------------------
# ホーム画面（カレンダー表示）
# --------------------------------------------
# home/views.py

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- 表示する年月を決定する ---
        # URLに year/month があればそれを使う。なければ今の年月を使う
        today = timezone.now()
        year = self.kwargs.get('year', today.year)
        month = self.kwargs.get('month', today.month)

        # --- 「前月」と「翌月」を計算する ---
        # カレンダーの ◁ ▷ ボタンのリンク先を作るために必要
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        # カレンダーの枠を作成（日曜始まり）
        cal = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)

        # テンプレートに渡すデータを更新
        context.update({
            "year": year,
            "month": month,
            "calendar": cal,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
        })

        # --- その月の収支データを取得 ---
        qs = Transaction.objects.filter(
            user=self.request.user,
            date__year=year,
            date__month=month,
        )

        # (日別合計の計算ロジックなどは以前のまま変更なし)
        income_by_day = qs.filter(tx_type=Transaction.INCOME).annotate(day=ExtractDay("date")).values("day").annotate(total=Sum("amount"))
        expense_by_day = qs.filter(tx_type=Transaction.EXPENSE).annotate(day=ExtractDay("date")).values("day").annotate(total=Sum("amount"))

        context["income_map"] = {row["day"]: row["total"] for row in income_by_day}
        context["expense_map"] = {row["day"]: row["total"] for row in expense_by_day}

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
        transactions = Transaction.objects.filter(
            user=request.user, 
            date=target_date
        ).values('id', 'tx_type', 'amount', 'memo').order_by('-id') # idの大きい順＝新しい順
        # リストを作成
        transactions_data = []
        for tx in transactions:
            transactions_data.append({
                'id': tx['id'], 
                'amount_str': f"{tx['amount']}円", # 金額だけにする
                'is_income': tx['tx_type'] == Transaction.INCOME, # 判定用にフラグを持たせる
                'memo': tx['memo']
            })
        
        # 辞書形式にして 'transactions' というキーで返す
        return JsonResponse({'transactions': transactions_data})
        


# ============================
# 収支登録ページ
# ============================
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "households/transaction_form.html"
    success_url = reverse_lazy('home:home')
    
    def get_initial(self):
    # 初期値に今日を設定
        initial = super().get_initial()
        date_str = self.request.GET.get('date')
        if date_str:
            initial['date'] = date_str
        else:
            initial['date'] = timezone.now().date()  # 今日の日付をデフォルトに
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