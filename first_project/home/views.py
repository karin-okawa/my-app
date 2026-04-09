# ①DjangoのView関連

 # Djangoの「テンプレートを表示するだけ」のView（HTMLを返すため）
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, View, DeleteView

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

 # home専用のTransactionFormを読み込む
from .forms import TransactionForm


from households.models import HouseholdAccount, UserHouseholdAccount

from django.contrib import messages

from django.shortcuts import redirect

import uuid





def get_current_household(request):
# 現在選択中の家計簿を返す関数。セッションに保存されていればそれを使い、なければユーザーの最初の家計簿を返す。
    
    # セッションから現在の家計簿IDを取得する
    household_id = request.session.get('current_household_id')
    
    # ユーザーが所属している家計簿を取得する
    user_households = UserHouseholdAccount.objects.filter(
        user=request.user,
        status=1
    ).select_related('household_account')

    if not user_households.exists():
        return None

    # セッションに家計簿IDがある場合はそれを使う
    if household_id:
        household = user_households.filter(
            household_account_id=household_id
        ).first()
        if household:
            return household.household_account

    # セッションになければ最初の家計簿をセッションに保存して返す
    first_household = user_households.first().household_account
    request.session['current_household_id'] = first_household.id
    return first_household


# --------------------------------------------
# ホーム画面（カレンダー表示）
# --------------------------------------------
# home/views.py

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 現在選択中の家計簿を取得する
        household = get_current_household(self.request)
        context['current_household'] = household

        # ユーザーが所属している全家計簿を取得する（切り替え用）
        user_households = UserHouseholdAccount.objects.filter(
            user=self.request.user,
            status=1
        ).select_related('household_account')
        context['user_households'] = user_households
        
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
            "current_day": today.day if (today.year == year and today.month == month) else None,
        })

        # 家計簿がない場合は空のデータを返す
        if not household:
            context.update({
                "income_map": {},
                "expense_map": {},
                "transactions": [],
                "total_income": 0,
                "total_expense": 0,
                "total_balance": 0,
                "income_image_days": set(),
                "expense_image_days": set(),
            })
            return context

        # 現在の家計簿に紐づいたその月の収支データを取得
        qs = Transaction.objects.filter(
            household_account=household,
            date__year=year,
            date__month=month,
        )

        # 日別合計の計算ロジック
        income_by_day = qs.filter(tx_type=Transaction.INCOME).annotate(day=ExtractDay("date")).values("day").annotate(total=Sum("amount"))
        expense_by_day = qs.filter(tx_type=Transaction.EXPENSE).annotate(day=ExtractDay("date")).values("day").annotate(total=Sum("amount"))

        context["income_map"] = {row["day"]: row["total"] for row in income_by_day}
        context["expense_map"] = {row["day"]: row["total"] for row in expense_by_day}

        # その月の収支一覧を日付の新しい順に取得する
        transactions = qs.order_by('-date', '-created_at').select_related('category')
        context['transactions'] = transactions

        # その月の収入・支出・合計を計算する
        total_income = qs.filter(tx_type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = qs.filter(tx_type=Transaction.EXPENSE).aggregate(total=Sum('amount'))['total'] or 0
        total_balance = total_income - total_expense
        context['total_income'] = total_income
        context['total_expense'] = total_expense
        context['total_balance'] = total_balance

        # 収入カテゴリーで画像がアップロードされている日を取得する
        income_image_days = qs.filter(
            image__isnull=False,
            tx_type=Transaction.INCOME
        ).exclude(
            image=''
        ).annotate(
            day=ExtractDay("date")
        ).values_list("day", flat=True).distinct()

        # 支出カテゴリーで画像がアップロードされている日を取得する
        expense_image_days = qs.filter(
            image__isnull=False,
            tx_type=Transaction.EXPENSE
        ).exclude(
            image=''
        ).annotate(
            day=ExtractDay("date")
        ).values_list("day", flat=True).distinct()

        # それぞれセットとして保持する
        context["income_image_days"] = set(income_image_days)
        context["expense_image_days"] = set(expense_image_days) 

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
        
        # 現在選択中の家計簿のデータのみ取得する
        household = get_current_household(request)
        
        # DBから指定した日の自分のデータを取得
        transactions = Transaction.objects.filter(
            household_account=household,
            date=target_date
        ).select_related('category').order_by('-id')
        
        # リストを作成
        transactions_data = []
        for tx in transactions:
            # カテゴリー名とメモを組み合わせて表示する（辞書の外で定義する）
            category_name = tx.category.name if tx.category else '未分類'
            memo_text = f'（{tx.memo}）' if tx.memo else ''
            transactions_data.append({
                'id': tx.id, 
                'amount_str': f"{tx.amount}円" if tx.amount else '',
                'is_income': tx.tx_type == Transaction.INCOME,
                'memo': category_name + memo_text,
                'has_image': bool(tx.image),
                'has_amount': bool(tx.amount),
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
    
    def get_form_kwargs(self):
        # フォームに現在の家計簿を渡す
        kwargs = super().get_form_kwargs()
        kwargs['household'] = get_current_household(self.request)
        return kwargs
    
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
        # 現在選択中の家計簿を取得して収支に紐づける
        household = get_current_household(self.request)
        form.instance.household_account = household
        # 登録したユーザーも記録する
        form.instance.user = self.request.user
        
        return super().form_valid(form)
        
                
        
        
# ============================
# 収支編集ページ
# ============================
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "households/transaction_form.html"
    success_url = reverse_lazy('home:home')
    
    def get_form_kwargs(self):
        # フォームに現在の家計簿を渡す
        kwargs = super().get_form_kwargs()
        kwargs['household'] = get_current_household(self.request)
        return kwargs
    
    def get_queryset(self):
        # 現在の家計簿に紐づいたデータだけを対象にする
        household = get_current_household(self.request)
        return Transaction.objects.filter(household_account=household)
    

# ============================
# 収支削除処理
# ============================
class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    # 収支を削除する
    model = Transaction
    # 削除後はホーム画面へ戻る
    success_url = reverse_lazy('home:home')

    def get_queryset(self):
        # 現在の家計簿に紐づいたデータだけを対象にする
        household = get_current_household(self.request)
        return Transaction.objects.filter(household_account=household)

    def get(self, request, *args, **kwargs):
        # GETリクエストでも即削除してリダイレクトする（確認画面なし）
        return self.delete(request, *args, **kwargs)
    

# ============================
# 家計簿切り替えView
# ============================
class HouseholdSwitchView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        household_id = request.POST.get('household_id')
        # ユーザーが所属している家計簿かどうか確認する
        if UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account_id=household_id,
            status=1
        ).exists():
            request.session['current_household_id'] = int(household_id)
        return redirect('home:home')


# ============================
# 家計簿新規作成View
# ============================
class HouseholdCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        if name:
            household = HouseholdAccount.objects.create(name=name)
            UserHouseholdAccount.objects.create(
                user=request.user,
                household_account=household,
                status=1,
                joined_at=timezone.now()
            )
            # デフォルトカテゴリーを作成する
            from households.models import Category
            default_categories = [
                {'name': '食費', 'category_type': 'expense', 'color': '#e74c3c', 'order': 1},
                {'name': '日用品費', 'category_type': 'expense', 'color': '#e67e22', 'order': 2},
                {'name': '衣服費', 'category_type': 'expense', 'color': '#f1c40f', 'order': 3},
                {'name': '交通費', 'category_type': 'expense', 'color': '#2ecc71', 'order': 4},
                {'name': '趣味費', 'category_type': 'expense', 'color': '#3498db', 'order': 5},
                {'name': '交際費', 'category_type': 'expense', 'color': '#9b59b6', 'order': 6},
                {'name': '固定費', 'category_type': 'expense', 'color': '#2c3e50', 'order': 7},
                {'name': 'その他', 'category_type': 'expense', 'color': '#95a5a6', 'order': 8},
                {'name': '給与', 'category_type': 'income', 'color': '#2ecc71', 'order': 1},
                {'name': 'その他', 'category_type': 'income', 'color': '#95a5a6', 'order': 2},
            ]
            for cat in default_categories:
                Category.objects.create(household_account=household, **cat)
            request.session['current_household_id'] = household.id
        return redirect('home:home')


# ============================
# 家計簿削除View
# ============================
class HouseholdDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        household_id = request.POST.get('household_id')
        uha = UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account_id=household_id,
            status=1
        ).first()
        if uha:
            uha.household_account.delete()
            request.session.pop('current_household_id', None)
        return redirect('home:home')


# ============================
# 家計簿名編集View
# ============================
class HouseholdUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        household_id = request.POST.get('household_id')
        name = request.POST.get('name', '').strip()
        uha = UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account_id=household_id,
            status=1
        ).first()
        if uha and name:
            uha.household_account.name = name
            uha.household_account.save()
        return redirect('home:home')