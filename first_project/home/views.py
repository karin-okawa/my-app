# ①DjangoのView関連
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, View, DeleteView  # 汎用ビュークラスのインポート
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須Mixinのインポート
from django.urls import reverse_lazy  # 名前付きURLパターンからURLを動的に生成する関数のインポート
from django.http import JsonResponse  # JSONレスポンス生成クラスのインポート

# ②便利ツール
import calendar  # Python標準ライブラリのカレンダー機能
from datetime import date  # 日付で絞り込むためのdateクラスのインポート
from django.utils import timezone  # タイムゾーン対応の日時取得モジュールのインポート
from django.db.models import Sum  # DB集計用（合計）関数のインポート
from django.db.models.functions import ExtractDay  # 日付から「日（1〜31）」だけを取り出す関数のインポート
import uuid  # ランダムなトークン生成モジュールのインポート
import hashlib  # ハッシュ化モジュールのインポート

# ③自分のアプリのモデルとフォーム
from households.models import Transaction, HouseholdAccount, UserHouseholdAccount, Category  # 家計簿アプリのモデルのインポート
from .forms import TransactionForm  # このアプリ内のフォームクラスのインポート
from django.contrib import messages  # メッセージ機能のインポート
from django.shortcuts import redirect, render  # リダイレクトと画面描画関数のインポート


def get_current_household(request):
    """
    現在選択中の家計簿を返す関数。
    セッションに保存されていればそれを使い、なければユーザーの最初の家計簿を返す。
    """
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


# ============================
# ホーム画面（カレンダー表示）
# ============================
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
        ).select_related('household_account').distinct()
        context['user_households'] = user_households

        # URLにyear/monthがあればそれを使い、なければ今の年月を使う
        today = timezone.now()
        year = self.kwargs.get('year', today.year)
        month = self.kwargs.get('month', today.month)

        # 前月・翌月を計算する（カレンダーの◁▷ボタンのリンク先に使用）
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

        # 現在の家計簿に紐づいたその月の収支データを取得する
        qs = Transaction.objects.filter(
            household_account=household,
            date__year=year,
            date__month=month,
        )

        # 日別合計の計算
        income_by_day = qs.filter(tx_type=Transaction.INCOME).annotate(day=ExtractDay("date")).values("day").annotate(total=Sum("amount"))
        expense_by_day = qs.filter(tx_type=Transaction.EXPENSE).annotate(day=ExtractDay("date")).values("day").annotate(total=Sum("amount"))

        context["income_map"] = {row["day"]: row["total"] for row in income_by_day}
        context["expense_map"] = {row["day"]: row["total"] for row in expense_by_day}

        # その月の収支一覧を日付の新しい順に取得する
        transactions = qs.order_by('-date', '-created_at').select_related('category')
        context['transactions'] = transactions

        # その月の収入・支出・差引残高を計算する
        total_income = qs.filter(tx_type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = qs.filter(tx_type=Transaction.EXPENSE).aggregate(total=Sum('amount'))['total'] or 0
        total_balance = total_income - total_expense
        context['total_income'] = total_income
        context['total_expense'] = total_expense
        context['total_balance'] = total_balance

        # 収入レコードで画像があり金額もある日を取得する（画像アイコン用）
        income_image_days = qs.filter(
            image__isnull=False,
            tx_type=Transaction.INCOME,
            amount__isnull=False,  # 金額がある場合のみ
        ).exclude(
            image=''
        ).annotate(
            day=ExtractDay("date")
        ).values_list("day", flat=True).distinct()

        # 収入レコードで画像はあるが金額がない日を取得する（びっくりマーク用）
        income_no_amount_days = qs.filter(
            image__isnull=False,
            tx_type=Transaction.INCOME,
            amount__isnull=True,  # 金額がない場合
        ).exclude(
            image=''
        ).annotate(
            day=ExtractDay("date")
        ).values_list("day", flat=True).distinct()

        # 支出レコードで画像があり金額もある日を取得する（画像アイコン用）
        expense_image_days = qs.filter(
            image__isnull=False,
            tx_type=Transaction.EXPENSE,
            amount__isnull=False,  # 金額がある場合のみ
        ).exclude(
            image=''
        ).annotate(
            day=ExtractDay("date")
        ).values_list("day", flat=True).distinct()

        # 支出レコードで画像はあるが金額がない日を取得する（びっくりマーク用）
        expense_no_amount_days = qs.filter(
            image__isnull=False,
            tx_type=Transaction.EXPENSE,
            amount__isnull=True,  # 金額がない場合
        ).exclude(
            image=''
        ).annotate(
            day=ExtractDay("date")
        ).values_list("day", flat=True).distinct()

        # それぞれセットとして保持する
        context["income_image_days"] = set(income_image_days)
        context["income_no_amount_days"] = set(income_no_amount_days)
        context["expense_image_days"] = set(expense_image_days)
        context["expense_no_amount_days"] = set(expense_no_amount_days)
   
       
        # 現在の家計簿の参加人数を取得する
        member_count = UserHouseholdAccount.objects.filter(
            household_account=household,
            status=1
        ).count()
        context['is_multi_member'] = member_count > 1
        
        # ユーザーごとの色を計算する（IDをもとに固定色を割り当てる）
        color_palette = [
            '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
            '#3498db', '#9b59b6', '#1abc9c', '#e91e63',
        ]
        user_colors = {}
        for tx in transactions:
            if tx.user and tx.user.id not in user_colors:
                user_colors[tx.user.id] = color_palette[tx.user.id % len(color_palette)]
        context['user_colors'] = user_colors

        # 家計簿リストを取得する際、最後に .distinct() を付け足す
        # これにより、同じ家計簿が複数回ヒットしても1つにまとめられる
        context['households'] = HouseholdAccount.objects.filter(
            userhouseholdaccount__user=self.request.user,
            userhouseholdaccount__status=1
        ).distinct()
        
        return context


# ============================
# 日別収支一覧ページ
# ============================
class DayTransactionListView(LoginRequiredMixin, ListView):
    """
    その日（YYYY/MM/DD）の収支(Transaction)だけを一覧表示するビュー
    ・ログインユーザーのデータだけ
    ・指定日付のデータだけ
    """
    model = Transaction
    template_name = "home/day_list.html"
    context_object_name = "transactions"

    def get_queryset(self):
        """
        URLから受け取ったyear/month/dayを使って日付を作り、
        その日付のTransactionだけを取得する
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
        テンプレートで「何日の日別詳細か」を表示できるようにする
        """
        context = super().get_context_data(**kwargs)
        context["year"] = int(self.kwargs["year"])
        context["month"] = int(self.kwargs["month"])
        context["day"] = int(self.kwargs["day"])
        return context


# ============================
# 日別収支データのJSON返却ビュー
# ============================
class DayTransactionJsonView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        y = self.kwargs['year']
        m = self.kwargs['month']
        d = self.kwargs['day']

        target_date = date(y, m, d)
        
        color_palette = [
          '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
          '#3498db', '#9b59b6', '#1abc9c', '#e91e63',
        ]

        # 現在選択中の家計簿のデータのみ取得する
        household = get_current_household(request)

        # 指定した日の収支データを取得する
        transactions = Transaction.objects.filter(
            household_account=household,
            date=target_date
        ).select_related('category').order_by('-id')

        # JSONに変換するリストを作成する
        transactions_data = []
        for tx in transactions:
            # カテゴリー名とメモを組み合わせて表示する
            category_name = tx.category.name if tx.category else '未分類'
            memo_text = f'（{tx.memo}）' if tx.memo else ''
            transactions_data.append({
                'id': tx.id,
                'amount_str': f"{tx.amount}円" if tx.amount else '',
                'is_income': tx.tx_type == Transaction.INCOME,
                'memo': category_name + memo_text,
                'has_image': bool(tx.image),
                'has_amount': bool(tx.amount),
                'avatar_url': tx.user.avatar.url if tx.user and tx.user.avatar else None,
                # ユーザーIDをもとに固定色を割り当てる
                'user_color': color_palette[tx.user.id % len(color_palette)] if tx.user else '#e0d5d0',
                'user_initial': tx.user.username[0] if tx.user and tx.user.username else '?',
            })

        # 現在の家計簿の参加人数を取得する
        member_count = UserHouseholdAccount.objects.filter(
            household_account=household,
            status=1
        ).count()
        return JsonResponse({
            'transactions': transactions_data,
            'is_multi_member': member_count > 1,  # 複数メンバーかどうか
        })


# ============================
# 収支登録ビュー
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
        # 日付の初期値を設定する（URLパラメーターがあればその日付、なければ今日）
        initial = super().get_initial()
        date_str = self.request.GET.get('date')
        if date_str:
            initial['date'] = date_str
        else:
            initial['date'] = timezone.now().date()
        return initial

    def form_valid(self, form):
        # 現在選択中の家計簿を取得して収支に紐づける
        household = get_current_household(self.request)
        form.instance.household_account = household
        # 登録したユーザーも記録する
        form.instance.user = self.request.user
        return super().form_valid(form)


# ============================
# 収支編集ビュー
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
# 収支削除ビュー
# ============================
class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    # 削除後はホーム画面へ戻る
    success_url = reverse_lazy('home:home')

    def get_queryset(self):
        # 現在の家計簿に紐づいたデータだけを対象にする
        household = get_current_household(self.request)
        return Transaction.objects.filter(household_account=household)

    def delete(self, request, *args, **kwargs):
        # サクセスメッセージを設定する
        messages.success(request, '収支を削除しました')
        # 親クラスの削除処理を実行する
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # GETリクエストでも即削除してリダイレクトする（確認画面なし）
        return self.delete(request, *args, **kwargs)


# ============================
# 家計簿切り替えビュー
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
            # セッションに選択した家計簿IDを保存する
            request.session['current_household_id'] = int(household_id)
        return redirect('home:home')


# ============================
# 家計簿新規作成ビュー
# ============================
class HouseholdCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        if name:
            # 1. すでに同じ名前の家計簿に自分が参加していないかチェック
            existing_link = UserHouseholdAccount.objects.filter(
                user=request.user,
                household_account__name=name,
                status=1
            ).first()

            if existing_link:
                # すでに存在する場合は、その家計簿を「選択中」にしてホームへ戻る
                request.session['current_household_id'] = existing_link.household_account.id
                return redirect('home:home')

            # 2. 存在しない場合のみ、新規作成処理を行う
            # 家計簿とユーザーの紐付けレコードを作成する
            household = HouseholdAccount.objects.create(name=name)
            UserHouseholdAccount.objects.create(
                user=request.user,
                household_account=household,
                status=1,
                joined_at=timezone.now()
            )
            # デフォルトカテゴリーを作成する
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
            
            # 作成した家計簿をセッションに保存する
            request.session['current_household_id'] = household.id

        return redirect('home:home')


# ============================
# 家計簿削除ビュー
# ============================
class HouseholdDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        household_id = request.POST.get('household_id')
        # ユーザーが所属している家計簿かどうか確認する
        uha = UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account_id=household_id,
            status=1
        ).first()
        if uha:
            # 家計簿本体を削除し、セッションからIDを削除する
            uha.household_account.delete()
            request.session.pop('current_household_id', None)
        return redirect('home:home')


# ============================
# 家計簿名編集ビュー
# ============================
class HouseholdUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        household_id = request.POST.get('household_id')
        name = request.POST.get('name', '').strip()
        # ユーザーが所属している家計簿かどうか確認する
        uha = UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account_id=household_id,
            status=1
        ).first()
        if uha and name:
            # 家計簿名を更新して保存する
            uha.household_account.name = name
            uha.household_account.save()
        return redirect('home:home')


# ============================
# 招待リンク発行ビュー
# ============================
class HouseholdInviteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        household_id = request.POST.get('household_id')

        # ユーザーが所属している家計簿かどうか確認する
        uha = UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account_id=household_id,
            status=1
        ).first()

        if not uha:
            return JsonResponse({'error': '権限がありません'}, status=403)

        # 招待トークンを生成してハッシュ化する
        token = str(uuid.uuid4())
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # 有効期限を30分後に設定する
        expires_at = timezone.now() + timezone.timedelta(minutes=30)

        # 既存の招待中レコードを削除する
        UserHouseholdAccount.objects.filter(
            household_account_id=household_id,
            status=2
        ).delete()

        # userを指定して作成する（Not Null制約エラーを防ぐため）
        UserHouseholdAccount.objects.create(
            user=request.user,
            household_account_id=household_id,
            invitation_token_hash=token_hash,
            expires_at=expires_at,
            status=2
        )

        # 招待URLを生成してJSONで返す
        invite_url = request.build_absolute_uri(
            f'/home/household/join/{token}/'
        )
        return JsonResponse({'invite_url': invite_url})


# ============================
# 招待リンクで家計簿に参加するビュー
# ============================
class HouseholdJoinView(View):
    def get(self, request, token, *args, **kwargs): 
        if not request.user.is_authenticated:
            request.session['invite_token'] = token
            return redirect('accounts:login')
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # 有効な招待レコードを検索
        invite_record = UserHouseholdAccount.objects.filter(
            invitation_token_hash=token_hash,
            status=2,
            expires_at__gt=timezone.now()
        ).first()

        if not invite_record:
            return render(request, 'home/invite_error.html', {
                'error': '招待リンクが無効または期限切れです'
            })

        # 招待用レコード自体の家計簿を取得しておく（削除前にキープ）
        target_household = invite_record.household_account

        # すでに参加しているかチェック
        existing_member = UserHouseholdAccount.objects.filter(
            user=request.user,
            household_account=target_household,
            status=1
        ).exists()

        if not existing_member:
            # まだ参加していない場合のみ新しいメンバーレコードを作成
            UserHouseholdAccount.objects.create(
                user=request.user,
                household_account=target_household,
                status=1,
                joined_at=timezone.now()
            )

        # 招待用レコード（status=2）を使い回さず、削除して失効させる
        invite_record.delete() 

        # 参加した家計簿をセッションに保存
        request.session['current_household_id'] = target_household.id

        return redirect('home:home')


# ============================
# グラフ画面ビュー
# ============================
class GraphView(LoginRequiredMixin, TemplateView):
    template_name = "home/graph.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在選択中の家計簿を取得する
        household = get_current_household(self.request)
        context['current_household'] = household

        # 表示する年月を決定する
        today = timezone.now()
        year = self.kwargs.get('year', today.year)
        month = self.kwargs.get('month', today.month)

        # 前月・翌月を計算する
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        context.update({
            'year': year,
            'month': month,
            'prev_year': prev_year,
            'prev_month': prev_month,
            'next_year': next_year,
            'next_month': next_month,
        })

        # 家計簿がない場合は空のデータを返す
        if not household:
            context.update({
                'expense_data': [],
                'income_data': [],
                'total_expense': 0,
                'total_income': 0,
            })
            return context

        # その月の収支データを取得する
        qs = Transaction.objects.filter(
            household_account=household,
            date__year=year,
            date__month=month,
        )

        # 支出のカテゴリー別集計
        expense_by_category = qs.filter(
            tx_type=Transaction.EXPENSE
        ).values(
            'category__name', 'category__color', 'category__order'
        ).annotate(
            total=Sum('amount')
        ).order_by('category__order')

        # 収入のカテゴリー別集計
        income_by_category = qs.filter(
            tx_type=Transaction.INCOME
        ).values(
            'category__name', 'category__color', 'category__order'
        ).annotate(
            total=Sum('amount')
        ).order_by('category__order')

        # テンプレートに渡すデータを整形する
        expense_data = [
            {
                'name': row['category__name'] or '未分類',
                'color': row['category__color'] or '#95a5a6',
                'total': row['total'] or 0,
            }
            for row in expense_by_category
        ]

        income_data = [
            {
                'name': row['category__name'] or '未分類',
                'color': row['category__color'] or '#95a5a6',
                'total': row['total'] or 0,
            }
            for row in income_by_category
        ]

        # 支出・収入の合計を計算する
        total_expense = sum(d['total'] for d in expense_data)
        total_income = sum(d['total'] for d in income_data)

        current_type = self.request.GET.get('type', 'expense')
        
        # テンプレート（HTML）に渡すデータをまとめて設定する
        context.update({
            'expense_data': expense_data,   # 支出のカテゴリー別集計リスト
            'income_data': income_data,     # 収入のカテゴリー別集計リスト
            'total_expense': total_expense, # 支出の合計金額
            'total_income': total_income,   # 収入の合計金額
            # 現在の表示タイプ（'expense' または 'income'）
            'current_type': current_type, 
        })
        
        return context