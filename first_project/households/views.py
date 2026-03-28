# ログインしていない人をログイン画面に飛ばすためのMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# 一覧表示・新規作成・更新・削除用の汎用CBV
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
# URL名からURLを作るための関数
from django.urls import reverse_lazy
# households/models.py のモデルを使う
from .models import Transaction, Category
# forms.py のフォームを使う
from .forms import TransactionForm
# JSONレスポンスを返すために使う
from django.http import JsonResponse
# 日付を扱うために使う
from datetime import date


# ============================
# 収支一覧ページ
# ============================
class TransactionListView(LoginRequiredMixin, ListView):
    # ログインユーザーの収支データだけを一覧表示する
    model = Transaction
    # 使用するテンプレート
    template_name = "households/transaction_list.html"
    # テンプレートで使う変数名
    context_object_name = "transactions"

    def get_queryset(self):
        # 自分のデータだけに絞り込む
        return Transaction.objects.filter(user=self.request.user)


# ============================
# 収支登録ページ
# ============================
class TransactionCreateView(LoginRequiredMixin, CreateView):
    # 収支登録画面
    model = Transaction
    # forms.pyの設定を使う
    form_class = TransactionForm
    # 使用するテンプレート
    template_name = "households/transaction_form.html"
    # 登録成功後 → 収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def form_valid(self, form):
        # 保存前にログインユーザーを自動設定
        form.instance.user = self.request.user
        return super().form_valid(form)


# ============================
# 収支編集ページ
# ============================
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    # 収支編集画面
    model = Transaction
    # forms.pyの設定を使う
    form_class = TransactionForm
    # 使用するテンプレート
    template_name = "households/transaction_form.html"
    # 編集成功後 → 収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def get_queryset(self):
        # 自分のデータだけを編集対象にする
        return Transaction.objects.filter(user=self.request.user)


# ============================
# 指定日付の収支データをJSONで返すAPI
# ============================
class DayTransactionsJsonView(LoginRequiredMixin, ListView):
    model = Transaction

    def get(self, request, *args, **kwargs):
        # URLから年月日を取得
        y = int(kwargs["year"])
        m = int(kwargs["month"])
        d = int(kwargs["day"])
        target = date(y, m, d)

        # 指定日付の自分のデータを取得
        qs = Transaction.objects.filter(
            user=request.user,
            date=target
        ).order_by("-created_at")

        # JSONに変換するデータを作成
        data = []
        for tx in qs:
            data.append({
                "id": tx.id,
                "tx_type": tx.tx_type,
                "tx_type_label": tx.get_tx_type_display(),
                "amount": tx.amount,
                "memo": tx.memo or "",
                "label": tx.memo or tx.get_tx_type_display(),
            })

        return JsonResponse({
            "date": target.isoformat(),
            "transactions": data,
        })


# ============================
# カテゴリー一覧ページ
# ============================
class CategoryListView(LoginRequiredMixin, ListView):
    # カテゴリーを一覧表示する
    model = Category
    # 使用するテンプレート
    template_name = "households/category_list.html"
    # テンプレートで使う変数名
    context_object_name = "categories"


# ============================
# カテゴリー新規作成ページ
# ============================
class CategoryCreateView(LoginRequiredMixin, CreateView):
    # カテゴリーを新規作成する
    model = Category
    # 入力項目：カテゴリー名・種類・色
    fields = ['name', 'category_type', 'color']
    # 使用するテンプレート
    template_name = "households/category_form.html"
    # 作成成功後 → カテゴリー一覧へ戻る
    success_url = reverse_lazy('households:category_list')


# ============================
# カテゴリー編集ページ
# ============================
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    # カテゴリーを編集する
    model = Category
    # 編集できる項目：カテゴリー名・種類・色
    fields = ['name', 'category_type', 'color']
    # 使用するテンプレート
    template_name = "households/category_form.html"
    # 編集成功後 → カテゴリー一覧へ戻る
    success_url = reverse_lazy('households:category_list')


# ============================
# カテゴリー削除ページ
# ============================
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    # カテゴリーを削除する
    model = Category
    # 使用するテンプレート
    template_name = "households/category_confirm_delete.html"
    # 削除成功後 → カテゴリー一覧へ戻る
    success_url = reverse_lazy('households:category_list')